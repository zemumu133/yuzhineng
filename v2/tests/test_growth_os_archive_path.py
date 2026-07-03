import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(r"D:\OpenClaw")
V2 = ROOT / "v2"
SCRIPT = V2 / "scripts" / "run_manufacturing_multi_agent_workflow.py"


def load_workflow_module():
    spec = importlib.util.spec_from_file_location("run_manufacturing_multi_agent_workflow_m1_1", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GrowthOSArchivePathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="m1-1-growthos-archive-"))
        self.projects_root = self.tmp / "projects"
        self.input_payload = {
            "company_location": "东莞",
            "factory_type": "包装厂",
            "product_name": "重型包装纸箱、物流包装、出口包装",
            "product_description": "东莞重型包装纸箱厂，面向电商仓储、制造工厂、物流公司和外贸企业。",
            "factory_capabilities": ["重型纸箱定制", "出口包装打样", "物流包装加固"],
            "target_customer_hint": ["电商仓储", "制造工厂", "物流公司", "外贸企业"],
            "platforms": ["小红书", "抖音", "公众号"],
            "mode": "draft_only",
            "search_required": False,
        }

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_ui_workflow_returns_main_project_archive_paths(self):
        workflow = load_workflow_module()

        result = workflow.run_workflow(
            self.input_payload,
            runs_root=self.tmp / "workflow-runs",
            collaboration_root=self.tmp / "multi-agent-runs",
            projects_root=self.projects_root,
            created_at="2026-07-03T16:30:00+0800",
            mirror_lobsterai_ui=False,
        )

        self.assertTrue(result["ok"])
        self.assertTrue(str(result["project_dir"]).startswith(str(self.projects_root)))
        self.assertEqual(result["projects_index_html"], str(self.projects_root / "projects_index.html"))
        self.assertTrue((self.projects_root / "index.html").exists())
        self.assertTrue((self.projects_root / "projects_index.html").exists())

        project_dir = Path(result["project_dir"])
        required_files = [
            "input.json",
            "project_manifest.json",
            "sources.json",
            "evidence.json",
            "lead_candidates.json",
            "leads.json",
            "action_intents.json",
            "approval_queue.json",
            "report.md",
            "handoff.docx",
            "safety_check.json",
            "review_report.md",
            "README_CN.md",
            "ui_delivery_items.json",
        ]
        for name in required_files:
            self.assertTrue((project_dir / name).exists(), name)

        manifest = json.loads((project_dir / "project_manifest.json").read_text(encoding="utf-8"))
        growth_os = manifest["growth_os"]
        self.assertTrue(growth_os["enabled"])
        self.assertFalse(growth_os["real_external_send"])
        self.assertEqual(growth_os["ui_delivery_items_path"], str(project_dir / "ui_delivery_items.json"))

        ui_items = json.loads((project_dir / "ui_delivery_items.json").read_text(encoding="utf-8"))
        item_types = {item["item_type"] for item in ui_items}
        display_areas = {item["display_area"] for item in ui_items}
        self.assertIn("action_intent", item_types)
        self.assertIn("approval", item_types)
        self.assertIn("handoff_document", item_types)
        self.assertNotIn("sidebar", display_areas)

        index_html = (self.projects_root / "projects_index.html").read_text(encoding="utf-8")
        self.assertIn("ActionIntent", index_html)
        self.assertIn("审批队列", index_html)
        self.assertIn("线索/商机", index_html)


if __name__ == "__main__":
    unittest.main()
