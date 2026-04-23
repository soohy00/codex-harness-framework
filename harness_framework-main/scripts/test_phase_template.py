"""
starter phase 템플릿 테스트.
"""

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = REPO_ROOT / "templates" / "phases-starter"


class PhaseTemplateTestCase(unittest.TestCase):
    def test_template_files_exist(self):
        self.assertTrue((TEMPLATE_ROOT / "README.md").exists())
        self.assertTrue((TEMPLATE_ROOT / "phases" / "index.json").exists())
        self.assertTrue((TEMPLATE_ROOT / "phases" / "0-setup" / "index.json").exists())
        self.assertTrue((TEMPLATE_ROOT / "phases" / "0-setup" / "step0.md").exists())
        self.assertTrue((TEMPLATE_ROOT / "phases" / "0-setup" / "step1.md").exists())

    def test_template_json_is_valid(self):
        top_index = json.loads((TEMPLATE_ROOT / "phases" / "index.json").read_text(encoding="utf-8"))
        phase_index = json.loads((TEMPLATE_ROOT / "phases" / "0-setup" / "index.json").read_text(encoding="utf-8"))

        self.assertEqual(top_index["phases"][0]["dir"], "0-setup")
        self.assertEqual(phase_index["steps"][0]["name"], "contracts")
        self.assertEqual(phase_index["steps"][1]["name"], "app-shell")

    def test_template_steps_do_not_reference_claude(self):
        for path in sorted((TEMPLATE_ROOT / "phases" / "0-setup").glob("step*.md")):
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("CLAUDE.md", content)

    def test_template_markdown_has_no_curly_placeholders(self):
        for path in sorted(TEMPLATE_ROOT.rglob("*.md")):
            content = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"\{[^}]+\}", content), msg=str(path))


if __name__ == "__main__":
    unittest.main()
