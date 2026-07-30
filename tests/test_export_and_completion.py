import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from export import ExportService


class ExportAndCompletionTests(unittest.TestCase):
    def test_markdown_export_includes_title_field(self):
        todos = [{"title": "示例任務", "content": "內容", "completion_history": []}]
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as handle:
            path = handle.name
        try:
            ExportService.export_to_markdown(todos, ["title", "content"], path=path)
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("## 示例任務", content)
            self.assertIn("- 說明：內容", content)
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_json_export_uses_selected_fields(self):
        todos = [{"title": "示例任務", "content": "內容", "category": "學習"}]
        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as handle:
            path = handle.name
        try:
            ExportService.export_to_json(todos, ["title", "content"], path=path)
            with open(path, "r", encoding="utf-8") as handle:
                exported = json.load(handle)
            self.assertEqual(exported[0], {"title": "示例任務", "content": "內容"})
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_markdown_export_skips_title_heading_when_title_field_unselected(self):
        todos = [{"title": "示例任務", "content": "內容"}]
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as handle:
            path = handle.name
        try:
            ExportService.export_to_markdown(todos, ["content"], path=path)
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
            self.assertNotIn("## 示例任務", content)
            self.assertIn("- 說明：內容", content)
        finally:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    unittest.main()
