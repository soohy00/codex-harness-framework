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

    def test_github_ci_exists(self):
        self.assertTrue((REPO_ROOT / ".github" / "workflows" / "ci.yml").exists())

    def test_readme_has_no_local_absolute_paths(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("/Users/", readme)
        self.assertNotIn("file://", readme)


if __name__ == "__main__":
    unittest.main()
