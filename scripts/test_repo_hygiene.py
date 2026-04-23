"""
공개 저장소 위생 테스트.
"""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class RepoHygieneTestCase(unittest.TestCase):
    def test_gitignore_blocks_env_and_local_artifacts(self):
        content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", content)
        self.assertIn(".env.*", content)
        self.assertIn(".DS_Store", content)
        self.assertIn("__pycache__/", content)
        self.assertIn(".worktrees/", content)

    def test_env_example_exists(self):
        self.assertTrue((REPO_ROOT / ".env.example").exists())

    def test_security_doc_exists(self):
        self.assertTrue((REPO_ROOT / "SECURITY.md").exists())

    def test_contributing_and_license_exist(self):
        self.assertTrue((REPO_ROOT / "CONTRIBUTING.md").exists())
        self.assertTrue((REPO_ROOT / "CONTRIBUTING.ko.md").exists())
        self.assertTrue((REPO_ROOT / "LICENSE").exists())

    def test_github_ci_exists(self):
        self.assertTrue((REPO_ROOT / ".github" / "workflows" / "ci.yml").exists())

    def test_readme_has_no_local_absolute_paths(self):
        for name in ["README.md", "README.ko.md"]:
            readme = (REPO_ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn("/Users/", readme)
            self.assertNotIn("file://", readme)

    def test_bilingual_readmes_exist_and_link_each_other(self):
        readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme_ko = (REPO_ROOT / "README.ko.md").read_text(encoding="utf-8")
        self.assertIn("./README.ko.md", readme_en)
        self.assertIn("./README.md", readme_ko)

    def test_bilingual_contributing_files_link_each_other(self):
        contributing_en = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        contributing_ko = (REPO_ROOT / "CONTRIBUTING.ko.md").read_text(encoding="utf-8")
        self.assertIn("./CONTRIBUTING.ko.md", contributing_en)
        self.assertIn("./CONTRIBUTING.md", contributing_ko)


if __name__ == "__main__":
    unittest.main()
