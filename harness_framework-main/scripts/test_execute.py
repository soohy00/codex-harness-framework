"""
execute.py의 핵심 동작을 검증하는 표준 라이브러리 테스트.
"""

import io
import json
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))
import execute as ex


class StepExecutorTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.root = Path(self.tmpdir.name)
        self.root_patcher = patch.object(ex, "ROOT", self.root)
        self.root_patcher.start()
        self.addCleanup(self.root_patcher.stop)

        self._write_project_files()
        self.executor = self._make_executor()

    def _write_project_files(self):
        phases_dir = self.root / "phases"
        phase_dir = phases_dir / "0-mvp"
        docs_dir = self.root / "docs"
        prompts_dir = self.root / "scripts" / "prompts"

        phase_dir.mkdir(parents=True)
        docs_dir.mkdir()
        prompts_dir.mkdir(parents=True)

        (self.root / "AGENTS.md").write_text(
            "\n".join(
                [
                    "# 프로젝트: TestProject",
                    "## ABSOLUTE 가드레일",
                    "- 기존 테스트를 깨뜨리지 마라.",
                    "- 타입 계약 파일의 인터페이스를 임의로 변경하지 마라.",
                ]
            ),
            encoding="utf-8",
        )

        (docs_dir / "PRD.md").write_text(
            "# PRD\n\n## 핵심 기능\n- 로그인\n- 대시보드\n",
            encoding="utf-8",
        )
        (docs_dir / "ARCHITECTURE.md").write_text(
            "# 아키텍처\n\n## 디렉토리 구조\nsrc/\n",
            encoding="utf-8",
        )
        (docs_dir / "ADR.md").write_text(
            "# ADR\n\n## 철학\n- 단순한 구조를 유지한다.\n",
            encoding="utf-8",
        )
        (docs_dir / "UI_GUIDE.md").write_text(
            "# UI\n\n## AI 슬롭 안티패턴\n- 과한 장식 금지\n",
            encoding="utf-8",
        )

        (prompts_dir / "implementer.md").write_text(
            "# Implementer\n\n당신은 Codex 구현 에이전트다.\n",
            encoding="utf-8",
        )
        (prompts_dir / "spec-reviewer.md").write_text(
            "# Spec Reviewer\n\nPASS 또는 FAIL로만 시작하라.\n",
            encoding="utf-8",
        )
        (prompts_dir / "quality-reviewer.md").write_text(
            "# Quality Reviewer\n\nPASS 또는 FAIL로만 시작하라.\n",
            encoding="utf-8",
        )

        top_index = {
            "phases": [
                {"dir": "0-mvp", "status": "pending"},
                {"dir": "1-polish", "status": "pending"},
            ]
        }
        (phases_dir / "index.json").write_text(
            json.dumps(top_index, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        phase_index = {
            "project": "TestProject",
            "phase": "mvp",
            "steps": [
                {"step": 0, "name": "setup", "status": "completed", "summary": "초기 설정 완료"},
                {"step": 1, "name": "core", "status": "completed", "summary": "핵심 로직 구현"},
                {"step": 2, "name": "ui", "status": "pending"},
            ],
        }
        (phase_dir / "index.json").write_text(
            json.dumps(phase_index, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (phase_dir / "step0.md").write_text("# Step 0\n\n설정합니다.\n", encoding="utf-8")
        (phase_dir / "step1.md").write_text("# Step 1\n\n핵심을 구현합니다.\n", encoding="utf-8")
        (phase_dir / "step2.md").write_text("# Step 2\n\nUI를 구현하세요.\n", encoding="utf-8")

    def _make_executor(self):
        return ex.StepExecutor("0-mvp")

    def test_stamp_returns_kst_timestamp(self):
        stamp = self.executor._stamp()
        self.assertIn("+0900", stamp)

    def test_load_absolute_rules_reads_agents_md(self):
        result = self.executor._load_absolute_rules()
        self.assertIn("ABSOLUTE 가드레일", result)
        self.assertIn("기존 테스트를 깨뜨리지 마라.", result)

    def test_build_step_context_includes_recent_completed_steps(self):
        index = self.executor._read_json(self.executor._index_file)
        result = self.executor._build_step_context(index)
        self.assertIn("Step 0 (setup): 초기 설정 완료", result)
        self.assertIn("Step 1 (core): 핵심 로직 구현", result)
        self.assertNotIn("ui", result)

    def test_build_preamble_includes_runtime_context(self):
        result = self.executor._build_preamble("RULES", "CONTEXT")
        self.assertIn("TestProject", result)
        self.assertIn("RULES", result)
        self.assertIn("phases/0-mvp/index.json", result)
        self.assertIn("feat(mvp):", result)

    def test_build_codex_command_uses_exec_mode(self):
        command = self.executor._build_codex_command(
            prompt="hello",
            model="gpt-5.4",
            sandbox_mode="workspace-write",
            output_path=self.root / "last-message.txt",
        )
        self.assertEqual(command[0:2], ["codex", "exec"])
        self.assertIn("--skip-git-repo-check", command)
        self.assertIn("--sandbox", command)
        self.assertIn("workspace-write", command)
        self.assertIn("--model", command)
        self.assertIn("gpt-5.4", command)

    def test_invoke_codex_writes_output_json(self):
        step = {"step": 2, "name": "ui"}

        def fake_run(cmd, **kwargs):
            output_path = Path(cmd[cmd.index("-o") + 1])
            output_path.write_text("완료했습니다.", encoding="utf-8")
            return MagicMock(returncode=0, stdout="trace output", stderr="")

        with patch("subprocess.run", side_effect=fake_run):
            output = self.executor._invoke_codex(step, "PREAMBLE\n", "gpt-5.4")

        self.assertEqual(output["agent"], "codex")
        self.assertEqual(output["exitCode"], 0)
        self.assertEqual(output["lastMessage"], "완료했습니다.")

        saved = json.loads((self.root / "phases" / "0-mvp" / "step2-output.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["model"], "gpt-5.4")
        self.assertEqual(saved["lastMessage"], "완료했습니다.")

    def test_invoke_codex_missing_step_file_exits(self):
        with self.assertRaises(SystemExit) as ctx:
            self.executor._invoke_codex({"step": 99, "name": "missing"}, "PREAMBLE", "gpt-5.4")
        self.assertEqual(ctx.exception.code, 1)

    def test_preflight_allows_non_git_repo(self):
        self.executor._git_enabled = False
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.executor._preflight_check()
        output = buffer.getvalue()
        self.assertIn("Pre-flight 통과", output)
        self.assertIn("Git 저장소가 없어", output)

    def test_preflight_rejects_push_without_git(self):
        self.executor._git_enabled = False
        self.executor._auto_push = True
        with self.assertRaises(SystemExit) as ctx:
            self.executor._preflight_check()
        self.assertEqual(ctx.exception.code, 1)

    def test_checkout_branch_skips_when_git_disabled(self):
        self.executor._git_enabled = False
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.executor._checkout_branch()
        self.assertIn("브랜치 작업을 생략합니다", buffer.getvalue())

    def test_commit_step_is_noop_without_git(self):
        self.executor._git_enabled = False
        self.executor._run_git = MagicMock()
        self.executor._commit_step(2, "ui")
        self.executor._run_git.assert_not_called()

    def test_update_top_index_marks_completed(self):
        self.executor._update_top_index("completed")
        top_index = json.loads((self.root / "phases" / "index.json").read_text(encoding="utf-8"))
        phase = next(item for item in top_index["phases"] if item["dir"] == "0-mvp")
        self.assertEqual(phase["status"], "completed")
        self.assertIn("completed_at", phase)

    def test_get_git_diff_falls_back_without_git(self):
        self.executor._git_enabled = False
        result = self.executor._get_git_diff()
        self.assertIn("git 저장소가 없어", result)

    def test_check_blockers_exits_on_error(self):
        index = self.executor._read_json(self.executor._index_file)
        index["steps"][2]["status"] = "error"
        index["steps"][2]["error_message"] = "실패"
        self.executor._write_json(self.executor._index_file, index)

        with self.assertRaises(SystemExit) as ctx:
            self.executor._check_blockers()
        self.assertEqual(ctx.exception.code, 1)

    def test_progress_indicator_records_elapsed_time(self):
        with ex.progress_indicator("test") as progress:
            time.sleep(0.15)
        self.assertGreaterEqual(progress.elapsed, 0.1)


class MainCliTestCase(unittest.TestCase):
    def test_missing_phase_dir_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "phases").mkdir()
            with patch("sys.argv", ["execute.py", "missing"]):
                with patch.object(ex, "ROOT", root):
                    with self.assertRaises(SystemExit) as ctx:
                        ex.main()
                    self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
