"""
Codex skill metadata 테스트.
"""

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"


class SkillMetadataTestCase(unittest.TestCase):
    def test_each_skill_has_openai_yaml(self):
        for skill_dir in sorted(SKILLS_ROOT.iterdir()):
            if not skill_dir.is_dir():
                continue
            self.assertTrue((skill_dir / "SKILL.md").exists())
            self.assertTrue((skill_dir / "agents" / "openai.yaml").exists())

    def test_openai_yaml_contains_required_fields(self):
        for skill_dir in sorted(SKILLS_ROOT.iterdir()):
            if not skill_dir.is_dir():
                continue

            skill_name = skill_dir.name
            raw = (skill_dir / "agents" / "openai.yaml").read_text(encoding="utf-8")

            self.assertIn("display_name:", raw)
            self.assertIn("short_description:", raw)
            self.assertIn("default_prompt:", raw)
            self.assertIn("allow_implicit_invocation: true", raw)
            self.assertIn(f"${skill_name}", raw)

            short_match = re.search(r'short_description:\s+"([^"]+)"', raw)
            self.assertIsNotNone(short_match)
            short_description = short_match.group(1)
            self.assertGreaterEqual(len(short_description), 25)
            self.assertLessEqual(len(short_description), 64)

            self.assertNotRegex(raw, r"\{[^}]+\}")


if __name__ == "__main__":
    unittest.main()
