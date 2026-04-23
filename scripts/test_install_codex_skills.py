"""
install_codex_skills.py 테스트.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import install_codex_skills as installer


class InstallCodexSkillsTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.root = Path(self.tmpdir.name)
        self.skills_root = self.root / "skills"
        self.skills_root.mkdir()
        self.target_root = self.root / "target"

        self._make_skill("alpha")
        self._make_skill("beta")

    def _make_skill(self, name: str):
        skill_dir = self.skills_root / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: test skill\n---\n",
            encoding="utf-8",
        )

    def test_discover_skills_finds_skill_dirs(self):
        skills = installer.discover_skills(self.skills_root)
        self.assertEqual([skill.name for skill in skills], ["alpha", "beta"])

    def test_install_skill_symlink_mode(self):
        source = self.skills_root / "alpha"
        status = installer.install_skill(source, self.target_root, mode="symlink")
        self.assertEqual(status, "installed")
        target = self.target_root / "alpha"
        self.assertTrue(target.is_symlink())
        self.assertEqual(target.resolve(), source.resolve())

    def test_install_skill_copy_mode(self):
        source = self.skills_root / "alpha"
        status = installer.install_skill(source, self.target_root, mode="copy")
        self.assertEqual(status, "installed")
        target = self.target_root / "alpha"
        self.assertTrue(target.exists())
        self.assertFalse(target.is_symlink())
        self.assertTrue((target / "SKILL.md").exists())

    def test_install_skill_skips_existing_without_force(self):
        source = self.skills_root / "alpha"
        installer.install_skill(source, self.target_root, mode="copy")
        status = installer.install_skill(source, self.target_root, mode="copy", force=False)
        self.assertEqual(status, "skipped")

    def test_install_skill_replaces_existing_with_force(self):
        source = self.skills_root / "alpha"
        installer.install_skill(source, self.target_root, mode="copy")
        replacement = source / "SKILL.md"
        replacement.write_text("---\nname: alpha\ndescription: changed\n---\n", encoding="utf-8")
        status = installer.install_skill(source, self.target_root, mode="copy", force=True)
        self.assertEqual(status, "installed")
        copied = (self.target_root / "alpha" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("changed", copied)

    def test_install_all_skills_returns_statuses(self):
        results = installer.install_all_skills(
            skills_root=self.skills_root,
            target_root=self.target_root,
            mode="copy",
        )
        self.assertEqual(results, [("alpha", "installed"), ("beta", "installed")])

    def test_get_codex_skills_dir_uses_codex_home(self):
        target = installer.get_codex_skills_dir({"CODEX_HOME": str(self.root / "codex-home")})
        self.assertEqual(target, self.root / "codex-home" / "skills")


if __name__ == "__main__":
    unittest.main()
