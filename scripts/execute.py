#!/usr/bin/env python3
"""
Codex Step Executor — phase 내 step을 순차 실행하고 자가 교정한다.

Usage:
    python3 scripts/execute.py <phase-dir> [--push] [--no-review]

Guardrail 계층 (step frontmatter의 complexity 기반 자동 조합):
    low    → Layer 0 (Absolute) + Layer 1 (Prescriptive)
    medium → Layer 0 (Absolute) + Layer 2 (Principle) + Layer 3 (Context ×2)
    high   → Layer 0 (Absolute) + Layer 2 (Principle) + Layer 3 (Context ×4)

모델 기본값 (index.json 또는 frontmatter로 오버라이드 가능):
    low    → gpt-5.4-mini
    medium → gpt-5.4
    high   → gpt-5.2

리뷰 기본값 (index.json 또는 frontmatter로 오버라이드 가능):
    low    → none
    medium → spec-only
    high   → full
"""

import argparse
import contextlib
import json
import re
import subprocess
import sys
import threading
import time
import types
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_MODEL = {
    "low":    "gpt-5.4-mini",
    "medium": "gpt-5.4",
    "high":   "gpt-5.2",
}

DEFAULT_REVIEW = {
    "low":    "none",
    "medium": "spec-only",
    "high":   "full",
}

DEFAULT_REVIEW_MODEL = "gpt-5.4"

SUMMARY_WINDOW   = 3   # rolling window: 최근 N개 step summary만 다음 step에 전달
MAX_REVIEW_RETRY = 2   # 리뷰 실패 시 재시도 횟수 (구현 재시도와 별도)


# ---------------------------------------------------------------------------
# Progress indicator
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def progress_indicator(label: str):
    frames = "◐◓◑◒"
    stop = threading.Event()
    t0 = time.monotonic()

    def _animate():
        idx = 0
        while not stop.wait(0.12):
            sec = int(time.monotonic() - t0)
            sys.stderr.write(f"\r{frames[idx % len(frames)]} {label} [{sec}s]")
            sys.stderr.flush()
            idx += 1
        sys.stderr.write("\r" + " " * (len(label) + 20) + "\r")
        sys.stderr.flush()

    th = threading.Thread(target=_animate, daemon=True)
    th.start()
    info = types.SimpleNamespace(elapsed=0.0)
    try:
        yield info
    finally:
        stop.set()
        th.join()
        info.elapsed = time.monotonic() - t0


# ---------------------------------------------------------------------------
# StepExecutor
# ---------------------------------------------------------------------------

class StepExecutor:
    MAX_RETRIES = 3
    FEAT_MSG  = "feat({phase}): step {num} — {name}"
    CHORE_MSG = "chore({phase}): step {num} output"
    TZ = timezone(timedelta(hours=9))

    def __init__(self, phase_dir_name: str, *, auto_push: bool = False, no_review: bool = False):
        self._root           = str(ROOT)
        self._phases_dir     = ROOT / "phases"
        self._phase_dir      = self._phases_dir / phase_dir_name
        self._phase_dir_name = phase_dir_name
        self._top_index_file = self._phases_dir / "index.json"
        self._auto_push      = auto_push
        self._no_review      = no_review

        if not self._phase_dir.is_dir():
            print(f"ERROR: {self._phase_dir} 디렉토리가 없습니다.")
            sys.exit(1)

        self._index_file = self._phase_dir / "index.json"
        if not self._index_file.exists():
            print(f"ERROR: {self._index_file} 파일이 없습니다.")
            sys.exit(1)

        idx = self._read_json(self._index_file)
        self._project    = idx.get("project", "project")
        self._phase_name = idx.get("phase", phase_dir_name)
        self._total      = len(idx["steps"])
        self._git_enabled = self._detect_git_repo()

    # -----------------------------------------------------------------------
    # Entry point
    # -----------------------------------------------------------------------

    def run(self):
        self._print_header()
        self._preflight_check()
        self._check_blockers()
        self._checkout_branch()
        self._ensure_created_at()
        self._execute_all_steps()
        self._finalize()

    # -----------------------------------------------------------------------
    # Utilities
    # -----------------------------------------------------------------------

    def _stamp(self) -> str:
        return datetime.now(self.TZ).strftime("%Y-%m-%dT%H:%M:%S%z")

    @staticmethod
    def _read_json(p: Path) -> dict:
        return json.loads(p.read_text(encoding="utf-8"))

    @staticmethod
    def _write_json(p: Path, data: dict):
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _detect_git_repo(self) -> bool:
        result = self._run_git("rev-parse", "--show-toplevel")
        return result.returncode == 0

    # -----------------------------------------------------------------------
    # Frontmatter 파싱 (YAML 라이브러리 없이)
    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_frontmatter(step_file: Path) -> dict:
        """Step 파일 상단의 --- ... --- frontmatter를 파싱한다."""
        content = step_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return {}
        end = content.find("\n---", 3)
        if end == -1:
            return {}
        fm_text = content[3:end].strip()

        result: dict = {}
        for line in fm_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1]
                items = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
                result[key] = items
            elif val:
                result[key] = val
        return result

    @staticmethod
    def _parse_list(val) -> list:
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            return [v.strip() for v in val.split(",") if v.strip()]
        return []

    # -----------------------------------------------------------------------
    # 4계층 가드레일 빌더
    # -----------------------------------------------------------------------

    def _build_guardrails(self, step_file: Path) -> str:
        """
        복잡도 기반 4계층 가드레일을 조합한다.

        Layer 0 (Absolute)    : 항상 주입. AGENTS.md의 ABSOLUTE 섹션만.
        Layer 1 (Prescriptive): low 전용. 정확한 규칙과 참조.
        Layer 2 (Principle)   : medium/high. 판단 기준을 주는 원칙.
        Layer 3 (Context)     : medium(×2) / high(×4). 판단에 필요한 배경.
        """
        meta       = self._parse_frontmatter(step_file)
        complexity = meta.get("complexity", "medium")
        sections   = []

        # --- Layer 0: Absolute (항상) ---
        absolute = self._load_absolute_rules()
        if absolute:
            sections.append(absolute)

        # --- Layer 1: Prescriptive (low 전용) ---
        if complexity == "low":
            refs = self._parse_list(meta.get("prescriptive", []))
            if refs:
                loaded = self._load_doc_sections(refs, "## PRESCRIPTIVE 규칙")
                if loaded:
                    sections.append(loaded)

        # --- Layer 2: Principle (medium / high) ---
        if complexity in ("medium", "high"):
            refs = self._parse_list(meta.get("principle", []))
            if refs:
                loaded = self._load_doc_sections(refs, "## PRINCIPLE 가이드")
                if loaded:
                    sections.append(loaded)

        # --- Layer 3: Context (복잡도에 비례) ---
        context_limit = {"low": 0, "medium": 2, "high": 4}.get(complexity, 2)
        if context_limit > 0:
            refs = self._parse_list(meta.get("context", []))[:context_limit]
            if refs:
                loaded = self._load_doc_sections(refs, "## CONTEXT")
                if loaded:
                    sections.append(loaded)

        return "\n\n---\n\n".join(sections)

    def _load_absolute_rules(self) -> str:
        """AGENTS.md에서 '## ABSOLUTE 가드레일' 섹션만 추출한다."""
        agents_md = ROOT / "AGENTS.md"
        if not agents_md.exists():
            return ""
        content = agents_md.read_text(encoding="utf-8")

        m = re.search(r"(## ABSOLUTE 가드레일.*?)(?=\n##|\Z)", content, re.DOTALL)
        if m:
            return f"## 절대 규칙 (위반 불가)\n\n{m.group(1).strip()}"

        # fallback: CRITICAL 항목만
        critical = [l.strip() for l in content.splitlines() if "CRITICAL:" in l]
        if critical:
            return "## 절대 규칙 (위반 불가)\n\n" + "\n".join(f"- {l}" for l in critical)
        return ""

    def _load_doc_sections(self, refs: list, header: str) -> str:
        """
        'doc_path' 또는 'doc_path#section' 형식의 참조 목록을 로드한다.
        docs/ 하위 또는 프로젝트 루트에서 탐색한다.
        """
        parts = []
        for ref in refs:
            path_str, section = (ref.split("#", 1) + [None])[:2]

            doc_path = ROOT / "docs" / path_str
            if not doc_path.exists():
                doc_path = ROOT / path_str
            if not doc_path.exists():
                continue

            content = doc_path.read_text(encoding="utf-8")

            if section:
                # {{1,3}} — f-string 안에서 리터럴 중괄호를 사용하려면 이중 중괄호 필요.
                # {1,3} 로 쓰면 Python이 tuple (1, 3)으로 평가해 패턴이 깨진다.
                pattern = rf"(?:^|\n)(#{{1,3}}\s+{re.escape(section)}.*?)(?=\n#{{1,3}}\s|\Z)"
                m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                excerpt = m.group(1).strip() if m else content[:600].strip()
                parts.append(f"[{path_str}#{section}]\n\n{excerpt}")
            else:
                parts.append(f"[{path_str}]\n\n{content.strip()}")

        if not parts:
            return ""
        return f"{header}\n\n" + "\n\n".join(parts)

    # -----------------------------------------------------------------------
    # 모델 라우팅
    # -----------------------------------------------------------------------

    def _get_step_model(self, step: dict, meta: dict) -> str:
        """우선순위: index.json model > frontmatter model > complexity 기본값."""
        if "model" in step:
            return step["model"]
        if "model" in meta:
            return meta["model"]
        return DEFAULT_MODEL.get(meta.get("complexity", "medium"), "gpt-5.4")

    # -----------------------------------------------------------------------
    # 리뷰 게이팅
    # -----------------------------------------------------------------------

    def _get_review_mode(self, step: dict, meta: dict) -> str:
        """우선순위: --no-review 플래그 > index.json review > frontmatter review > complexity 기본값."""
        if self._no_review:
            return "none"
        if "review" in step:
            return str(step["review"])
        if "review" in meta:
            return str(meta["review"])
        return DEFAULT_REVIEW.get(meta.get("complexity", "medium"), "none")

    # -----------------------------------------------------------------------
    # Git
    # -----------------------------------------------------------------------

    def _run_git(self, *args) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(["git"] + list(args), cwd=self._root, capture_output=True, text=True)
        except FileNotFoundError:
            return subprocess.CompletedProcess(["git"] + list(args), 127, "", "git not found")

    def _checkout_branch(self):
        if not self._git_enabled:
            print("  Git   : 저장소 없음. 브랜치 작업을 생략합니다.")
            return

        branch = f"feat-{self._phase_name}"
        r = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        if r.returncode != 0:
            print(f"  ERROR: git을 사용할 수 없습니다.\n  {r.stderr.strip()}")
            sys.exit(1)
        if r.stdout.strip() == branch:
            return
        r = self._run_git("rev-parse", "--verify", branch)
        r = (self._run_git("checkout", branch)
             if r.returncode == 0
             else self._run_git("checkout", "-b", branch))
        if r.returncode != 0:
            print(f"  ERROR: 브랜치 '{branch}' checkout 실패.\n  {r.stderr.strip()}")
            sys.exit(1)
        print(f"  Branch: {branch}")

    def _commit_step(self, step_num: int, step_name: str):
        if not self._git_enabled:
            return

        output_rel = f"phases/{self._phase_dir_name}/step{step_num}-output.json"
        index_rel  = f"phases/{self._phase_dir_name}/index.json"

        self._run_git("add", "-A")
        self._run_git("reset", "HEAD", "--", output_rel)
        self._run_git("reset", "HEAD", "--", index_rel)

        if self._run_git("diff", "--cached", "--quiet").returncode != 0:
            msg = self.FEAT_MSG.format(phase=self._phase_name, num=step_num, name=step_name)
            r = self._run_git("commit", "-m", msg)
            if r.returncode == 0:
                print(f"  Commit: {msg}")
            else:
                print(f"  WARN: 코드 커밋 실패: {r.stderr.strip()}")

        self._run_git("add", "-A")
        if self._run_git("diff", "--cached", "--quiet").returncode != 0:
            msg = self.CHORE_MSG.format(phase=self._phase_name, num=step_num)
            r = self._run_git("commit", "-m", msg)
            if r.returncode != 0:
                print(f"  WARN: housekeeping 커밋 실패: {r.stderr.strip()}")

    # -----------------------------------------------------------------------
    # Top-level index
    # -----------------------------------------------------------------------

    def _update_top_index(self, status: str):
        if not self._top_index_file.exists():
            return
        top = self._read_json(self._top_index_file)
        ts  = self._stamp()
        for phase in top.get("phases", []):
            if phase.get("dir") == self._phase_dir_name:
                phase["status"] = status
                ts_key = {"completed": "completed_at", "error": "failed_at", "blocked": "blocked_at"}.get(status)
                if ts_key:
                    phase[ts_key] = ts
                break
        self._write_json(self._top_index_file, top)

    # -----------------------------------------------------------------------
    # Pre-flight 체크
    # -----------------------------------------------------------------------

    def _preflight_check(self):
        """실행 전 환경을 검증한다. 문제 발견 시 조기 종료."""
        errors = []
        index  = self._read_json(self._index_file)

        # step 파일 존재 확인
        for s in index["steps"]:
            step_file = self._phase_dir / f"step{s['step']}.md"
            if not step_file.exists():
                errors.append(f"step{s['step']}.md 파일이 없습니다.")

        # docs 플레이스홀더 확인 ({...} 패턴)
        docs_dir = ROOT / "docs"
        if docs_dir.is_dir():
            for doc in sorted(docs_dir.glob("*.md")):
                content = doc.read_text(encoding="utf-8")
                # <!-- ... --> 주석 안의 플레이스홀더는 무시
                stripped = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
                if re.search(r"\{[^}]{1,80}\}", stripped):
                    errors.append(f"{doc.name}에 미완성 플레이스홀더가 있습니다.")

        # git 상태 확인 (--push 사용 시에는 필수)
        if self._auto_push and not self._git_enabled:
            errors.append("--push를 사용하려면 git 저장소가 필요합니다.")

        if errors:
            print(f"\n  ✗ Pre-flight 실패 — 아래를 해결한 뒤 재실행하세요:")
            for e in errors:
                print(f"    · {e}")
            sys.exit(1)

        print(f"  ✓ Pre-flight 통과")
        if not self._git_enabled:
            print(f"  ! Git 저장소가 없어 브랜치, 커밋, diff 기반 리뷰를 생략합니다.")

    # -----------------------------------------------------------------------
    # Step context (rolling window)
    # -----------------------------------------------------------------------

    def _build_step_context(self, index: dict) -> str:
        """완료된 step 중 최근 SUMMARY_WINDOW개의 summary만 포함한다."""
        completed = [
            s for s in index["steps"]
            if s["status"] == "completed" and s.get("summary")
        ]
        recent = completed[-SUMMARY_WINDOW:]
        if not recent:
            return ""
        lines = [f"- Step {s['step']} ({s['name']}): {s['summary']}" for s in recent]
        return f"## 최근 완료 Step 요약 (최근 {SUMMARY_WINDOW}개)\n\n" + "\n".join(lines) + "\n\n"

    # -----------------------------------------------------------------------
    # Preamble 생성
    # -----------------------------------------------------------------------

    def _build_preamble(self, guardrails: str, step_context: str,
                        prev_error: Optional[str] = None) -> str:
        """
        프롬프트 구조:
          1. implementer.md  — 에이전트 역할·원칙·완료 기준 (사용자 수정 가능)
          2. 가드레일        — 복잡도 기반 제약 (ABSOLUTE 항상 + layer 1~3 선택)
          3. 이전 step 요약  — rolling window (최근 3개)
          4. 재시도 에러     — 있는 경우만
          5. 실행 컨텍스트   — 이번 실행에만 유효한 런타임 정보 (경로, 횟수, 커밋 형식)
        """
        # 1. implementer.md 로드 (없으면 최소 식별자만)
        impl_file = ROOT / "scripts" / "prompts" / "implementer.md"
        agent_spec = (
            impl_file.read_text(encoding="utf-8").strip()
            if impl_file.exists()
            else f"당신은 {self._project} 프로젝트를 맡은 Codex 구현 에이전트다."
        )

        # 4. 재시도 에러
        retry_section = ""
        if prev_error:
            retry_section = (
                f"\n## ⚠ 이전 시도 실패 — 아래 에러를 반드시 참고하여 수정하라\n\n"
                f"{prev_error}\n\n---\n\n"
            )

        # 5. 런타임 컨텍스트 (경로·횟수·형식은 실행 시점에만 확정됨)
        commit_example = self.FEAT_MSG.format(phase=self._phase_name, num="N", name="<step-name>")
        runtime_ctx = (
            f"## 실행 컨텍스트\n\n"
            f"- 프로젝트: {self._project}\n"
            f"- index.json 경로: `phases/{self._phase_dir_name}/index.json`\n"
            f"- 최대 재시도 횟수: {self.MAX_RETRIES}회\n"
            f"- git 저장소: {'있음' if self._git_enabled else '없음'}\n"
            f"- 커밋 형식: `{commit_example}`\n"
        )

        return (
            agent_spec      + "\n\n---\n\n"
            + guardrails    + "\n\n---\n\n"
            + step_context
            + retry_section
            + runtime_ctx   + "\n\n---\n\n"
        )

    # -----------------------------------------------------------------------
    # Codex 호출
    # -----------------------------------------------------------------------

    @staticmethod
    def _read_optional_text(path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def _build_codex_command(self, *, prompt: str, model: str, sandbox_mode: str,
                             output_path: Path) -> list[str]:
        return [
            "codex", "exec",
            "--skip-git-repo-check",
            "--sandbox", sandbox_mode,
            "--color", "never",
            "--model", model,
            "-o", str(output_path),
            prompt,
        ]

    def _invoke_codex(self, step: dict, preamble: str, model: str) -> dict:
        step_num, step_name = step["step"], step["name"]
        step_file = self._phase_dir / f"step{step_num}.md"
        if not step_file.exists():
            print(f"\n  ERROR: {step_file} 파일이 없습니다.")
            sys.exit(1)

        prompt = preamble + step_file.read_text(encoding="utf-8")
        message_path = self._phase_dir / f"step{step_num}-last-message.txt"
        cmd = self._build_codex_command(
            prompt=prompt,
            model=model,
            sandbox_mode="workspace-write",
            output_path=message_path,
        )
        try:
            result = subprocess.run(
                cmd,
                cwd=self._root, capture_output=True, text=True, timeout=1800,
            )
            stdout, stderr, exit_code = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            print(f"\n  WARN: Codex 시간 초과 (1800s) — step {step_num} 재시도 대상")
            stdout, stderr, exit_code = "", "TimeoutExpired: 1800s 초과", -1

        if exit_code != 0:
            print(f"\n  WARN: Codex 비정상 종료 (code {exit_code})")
            if stderr:
                print(f"  stderr: {stderr[:400]}")

        output = {
            "step": step_num, "name": step_name, "agent": "codex", "model": model,
            "exitCode": exit_code,
            "stdout": stdout, "stderr": stderr,
            "lastMessage": self._read_optional_text(message_path),
        }
        out_path = self._phase_dir / f"step{step_num}-output.json"
        out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        return output

    # -----------------------------------------------------------------------
    # 리뷰 에이전트
    # -----------------------------------------------------------------------

    def _get_git_diff(self) -> str:
        """
        리뷰 시점의 코드 변경사항을 반환한다.

        우선순위:
        1. 마지막 커밋의 변경사항 (implementer가 커밋 완료한 경우)
        2. 워킹트리 변경사항 (implementer가 커밋 전인 경우)
        3. staged 변경사항
        """
        if not self._git_enabled:
            return "## 변경된 코드\n\n(git 저장소가 없어 diff를 제공하지 못했다. 리뷰어는 현재 파일 상태만으로 판단한다.)"

        # 1순위: 마지막 커밋 내용 (implementer가 커밋 완료한 후 리뷰하는 일반 케이스)
        r = self._run_git("diff", "HEAD~1", "HEAD")
        if r.returncode == 0 and r.stdout.strip():
            diff = r.stdout.strip()
            stat_r = self._run_git("diff", "--stat", "HEAD~1", "HEAD")
            stat = stat_r.stdout.strip() if stat_r.returncode == 0 else ""
            if len(diff) > 3000:
                diff = diff[:3000] + "\n\n... (diff truncated)"
            return f"## 변경된 코드 (마지막 커밋)\n\n```diff\n{diff}\n```\n\n파일 통계:\n{stat}"

        # 2순위: 워킹트리 변경사항 (커밋 전 상태)
        r = self._run_git("diff", "HEAD", "--", "src/", "app/", "lib/", "components/")
        if r.returncode == 0 and r.stdout.strip():
            diff = r.stdout.strip()
            if len(diff) > 3000:
                diff = diff[:3000] + "\n\n... (diff truncated)"
            return f"## 변경된 코드 (미커밋 변경사항)\n\n```diff\n{diff}\n```"

        # 3순위: staged 변경사항
        r = self._run_git("diff", "--cached")
        if r.returncode == 0 and r.stdout.strip():
            diff = r.stdout.strip()[:3000]
            return f"## 변경된 코드 (staged)\n\n```diff\n{diff}\n```"

        return "## 변경된 코드\n\n(변경사항 없음 — 리뷰어는 step 명세만으로 판단한다)"

    def _invoke_reviewer(self, prompt_file: Path, step: dict,
                         reviewer_type: str, ref_docs: list[str]) -> tuple[bool, str]:
        """
        리뷰 에이전트를 실행한다.
        반환: (passed: bool, reason: str) — FAIL 시 reason에 리뷰어 출력 포함.
        ref_docs: 이 리뷰어에게 필요한 문서 목록 (선택적 주입).
        """
        step_num  = step["step"]
        step_file = self._phase_dir / f"step{step_num}.md"
        if not step_file.exists() or not prompt_file.exists():
            return True, ""

        # 역할별 필요 문서만 주입 (전체 docs 금지)
        doc_context = self._load_doc_sections(ref_docs, "## 참고 문서") if ref_docs else ""
        diff_context = self._get_git_diff()

        review_prompt = (
            prompt_file.read_text(encoding="utf-8")
            + "\n\n---\n\n"
            + f"## 검토 대상 Step 명세\n\n{step_file.read_text(encoding='utf-8')}\n\n"
            + diff_context + "\n\n"
            + doc_context
        )

        tag = f"Review ({reviewer_type}) step {step_num}"
        review_output_path = self._phase_dir / f"step{step_num}-{reviewer_type}-review.txt"
        try:
            with progress_indicator(tag):
                result = subprocess.run(
                    self._build_codex_command(
                        prompt=review_prompt,
                        model=DEFAULT_REVIEW_MODEL,
                        sandbox_mode="read-only",
                        output_path=review_output_path,
                    ),
                    cwd=self._root, capture_output=True, text=True, timeout=600,
                )
        except subprocess.TimeoutExpired:
            print(f"  WARN: 리뷰어 시간 초과 ({reviewer_type}) — PASS로 처리")
            return True, ""

        if result.returncode != 0:
            print(f"  WARN: 리뷰어 비정상 종료 ({reviewer_type}) — PASS로 처리")
            return True, ""

        review_text = self._read_optional_text(review_output_path).strip() or result.stdout.strip()

        # PASS/FAIL 판정: 첫 단어 기준으로만 매칭
        first_word = review_text.split()[0].upper() if review_text else ""
        if first_word == "FAIL":
            snippet = review_text[:500].strip()
            print(f"  ✗ {reviewer_type} review FAIL:\n    {snippet}")
            return False, f"[{reviewer_type} 리뷰 FAIL]\n{snippet}"

        print(f"  ✓ {reviewer_type} review PASS")
        return True, ""

    def _run_review(self, step: dict, review_mode: str) -> tuple[bool, str]:
        """
        리뷰 파이프라인 실행.
        반환: (passed: bool, reason: str) — FAIL 시 reason에 리뷰어 출력 포함.
        리뷰 재시도(MAX_REVIEW_RETRY)는 구현 재시도와 별도로 관리한다.
        """
        if review_mode == "none":
            return True, ""

        prompts_dir = ROOT / "scripts" / "prompts"
        last_reason = ""

        # spec-reviewer: PRD 핵심기능 + ARCHITECTURE 구조만 주입
        spec_file = prompts_dir / "spec-reviewer.md"
        if spec_file.exists():
            for attempt in range(1, MAX_REVIEW_RETRY + 1):
                passed, reason = self._invoke_reviewer(
                    spec_file, step, "spec",
                    ref_docs=["PRD.md#핵심 기능", "ARCHITECTURE.md#디렉토리 구조"],
                )
                if passed:
                    break
                last_reason = reason
                if attempt == MAX_REVIEW_RETRY:
                    return False, last_reason
                print(f"  ↻ spec review retry {attempt}/{MAX_REVIEW_RETRY}")

        if review_mode != "full":
            return True, ""

        # quality-reviewer: ADR 전체 + UI_GUIDE 안티패턴 주입
        # ADR#철학만 주입하면 구체적인 기술 결정(금지 패턴 등) 판단 불가 → 전체 주입
        quality_file = prompts_dir / "quality-reviewer.md"
        if quality_file.exists():
            for attempt in range(1, MAX_REVIEW_RETRY + 1):
                passed, reason = self._invoke_reviewer(
                    quality_file, step, "quality",
                    ref_docs=["ADR.md", "UI_GUIDE.md#AI 슬롭 안티패턴"],
                )
                if passed:
                    break
                last_reason = reason
                if attempt == MAX_REVIEW_RETRY:
                    return False, last_reason
                print(f"  ↻ quality review retry {attempt}/{MAX_REVIEW_RETRY}")

        return True, ""

    # -----------------------------------------------------------------------
    # 헤더 & 초기 검증
    # -----------------------------------------------------------------------

    def _print_header(self):
        review_label = "disabled (--no-review)" if self._no_review else "auto (complexity 기반)"
        print(f"\n{'='*62}")
        print(f"  Codex Step Executor")
        print(f"  Phase : {self._phase_name}  |  Steps: {self._total}")
        print(f"  Agent : Codex")
        print(f"  Review: {review_label}")
        print(f"  Git   : {'enabled' if self._git_enabled else 'disabled'}")
        if self._auto_push:
            print(f"  Push  : enabled")
        print(f"{'='*62}")

    def _check_blockers(self):
        index = self._read_json(self._index_file)
        for s in reversed(index["steps"]):
            if s["status"] == "error":
                print(f"\n  ✗ Step {s['step']} ({s['name']}) 실패.")
                print(f"  Error: {s.get('error_message', 'unknown')}")
                print(f"  index.json에서 status를 'pending'으로 바꾸고 재실행하세요.")
                sys.exit(1)
            if s["status"] == "blocked":
                print(f"\n  ⏸ Step {s['step']} ({s['name']}) 차단됨.")
                print(f"  Reason: {s.get('blocked_reason', 'unknown')}")
                print(f"  사유를 해결하고 status를 'pending'으로 바꾸세요.")
                sys.exit(2)
            if s["status"] != "pending":
                break

    def _ensure_created_at(self):
        index = self._read_json(self._index_file)
        if "created_at" not in index:
            index["created_at"] = self._stamp()
            self._write_json(self._index_file, index)

    # -----------------------------------------------------------------------
    # 실행 루프
    # -----------------------------------------------------------------------

    def _execute_single_step(self, step: dict) -> bool:
        """단일 step 실행 (재시도 포함). 완료 시 True."""
        step_num, step_name = step["step"], step["name"]
        step_file = self._phase_dir / f"step{step_num}.md"

        meta        = self._parse_frontmatter(step_file)
        model       = self._get_step_model(step, meta)
        review_mode = self._get_review_mode(step, meta)
        guardrails  = self._build_guardrails(step_file)
        complexity  = meta.get("complexity", "medium")

        prev_error = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            index        = self._read_json(self._index_file)
            step_context = self._build_step_context(index)
            preamble     = self._build_preamble(guardrails, step_context, prev_error)

            model_short = model.split("-")[1][:3] if "-" in model else model[:6]
            tag = f"Step {step_num}/{self._total - 1} [{complexity}/{model_short}]: {step_name}"
            if attempt > 1:
                tag += f" [retry {attempt}/{self.MAX_RETRIES}]"

            with progress_indicator(tag) as pi:
                self._invoke_codex(step, preamble, model)
            elapsed = int(pi.elapsed)  # with 블록 밖에서 읽어야 finally가 설정한 값을 얻는다

            # --- 상태 확인 ---
            index  = self._read_json(self._index_file)
            status = next(
                (s.get("status", "pending") for s in index["steps"] if s["step"] == step_num),
                "pending",
            )
            ts = self._stamp()

            if status == "completed":
                for s in index["steps"]:
                    if s["step"] == step_num:
                        s["completed_at"] = ts
                self._write_json(self._index_file, index)

                # 리뷰 실행
                review_passed, review_reason = self._run_review(step, review_mode)
                if not review_passed:
                    # 리뷰 실패 → pending으로 되돌리고 재시도
                    index = self._read_json(self._index_file)
                    for s in index["steps"]:
                        if s["step"] == step_num:
                            s["status"] = "pending"
                            s.pop("completed_at", None)
                    self._write_json(self._index_file, index)
                    prev_error = review_reason or f"리뷰 실패 (attempt {attempt}): 스펙 또는 품질 기준 미충족"
                    continue

                self._commit_step(step_num, step_name)
                print(f"  ✓ Step {step_num}: {step_name} [{elapsed}s] (model: {model})")
                return True

            if status == "blocked":
                for s in index["steps"]:
                    if s["step"] == step_num:
                        s["blocked_at"] = ts
                self._write_json(self._index_file, index)
                reason = next(
                    (s.get("blocked_reason", "") for s in index["steps"] if s["step"] == step_num), ""
                )
                print(f"  ⏸ Step {step_num}: {step_name} blocked [{elapsed}s]")
                print(f"    Reason: {reason}")
                self._update_top_index("blocked")
                sys.exit(2)

            # error 또는 status 미업데이트
            err_msg = next(
                (s.get("error_message", "status가 업데이트되지 않음")
                 for s in index["steps"] if s["step"] == step_num),
                "status가 업데이트되지 않음",
            )

            if attempt < self.MAX_RETRIES:
                for s in index["steps"]:
                    if s["step"] == step_num:
                        s["status"] = "pending"
                        s.pop("error_message", None)
                self._write_json(self._index_file, index)
                prev_error = err_msg
                print(f"  ↻ Step {step_num}: retry {attempt}/{self.MAX_RETRIES} — {err_msg}")
            else:
                for s in index["steps"]:
                    if s["step"] == step_num:
                        s["status"]        = "error"
                        s["error_message"] = f"[{self.MAX_RETRIES}회 시도 후 실패] {err_msg}"
                        s["failed_at"]     = ts
                self._write_json(self._index_file, index)
                self._commit_step(step_num, step_name)
                print(f"  ✗ Step {step_num}: {step_name} 실패 ({self.MAX_RETRIES}회) [{elapsed}s]")
                print(f"    Error: {err_msg}")
                self._update_top_index("error")
                sys.exit(1)

        return False  # unreachable

    def _execute_all_steps(self):
        while True:
            index   = self._read_json(self._index_file)
            pending = next((s for s in index["steps"] if s["status"] == "pending"), None)
            if pending is None:
                print("\n  All steps completed!")
                return

            step_num = pending["step"]
            for s in index["steps"]:
                if s["step"] == step_num and "started_at" not in s:
                    s["started_at"] = self._stamp()
                    self._write_json(self._index_file, index)
                    break

            self._execute_single_step(pending)

    def _finalize(self):
        index = self._read_json(self._index_file)
        index["completed_at"] = self._stamp()
        self._write_json(self._index_file, index)
        self._update_top_index("completed")

        if self._git_enabled:
            self._run_git("add", "-A")
            if self._run_git("diff", "--cached", "--quiet").returncode != 0:
                msg = f"chore({self._phase_name}): mark phase completed"
                r   = self._run_git("commit", "-m", msg)
                if r.returncode == 0:
                    print(f"  ✓ {msg}")

            if self._auto_push:
                branch = f"feat-{self._phase_name}"
                r = self._run_git("push", "-u", "origin", branch)
                if r.returncode != 0:
                    print(f"\n  ERROR: git push 실패: {r.stderr.strip()}")
                    sys.exit(1)
                print(f"  ✓ Pushed to origin/{branch}")

        print(f"\n{'='*62}")
        print(f"  Phase '{self._phase_name}' 완료!")
        print(f"{'='*62}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Codex Step Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("phase_dir",    help="Phase 디렉토리명 (예: 0-mvp)")
    parser.add_argument("--push",       action="store_true", help="완료 후 origin에 push")
    parser.add_argument("--no-review",  action="store_true", help="리뷰 에이전트 비활성화")
    args = parser.parse_args()

    StepExecutor(args.phase_dir, auto_push=args.push, no_review=args.no_review).run()


if __name__ == "__main__":
    main()
