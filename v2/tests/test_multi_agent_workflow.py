import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(r"D:\OpenClaw")
SCRIPT = ROOT / "v2" / "scripts" / "run_manufacturing_multi_agent_workflow.py"


def load_workflow_module():
    spec = importlib.util.spec_from_file_location("run_manufacturing_multi_agent_workflow", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ManufacturingMultiAgentWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="phase2e-multi-agent-"))
        self.runs_root = self.tmp / "workflow-runs"
        self.projects_root = self.tmp / "projects"
        self.input_payload = {
            "company_location": "东莞",
            "factory_type": "电子配件厂",
            "product_name": "电子连接件、线束、充电配件",
            "product_description": "面向电子厂、品牌商、跨境卖家和维修渠道的电子连接件、线束、充电配件。",
            "factory_capabilities": ["连接件加工", "线束打样", "充电配件组装", "小批量试产"],
            "target_customer_hint": ["电子厂", "品牌商", "跨境卖家", "维修渠道"],
            "platforms": ["小红书", "抖音", "公众号"],
            "mode": "draft_only",
            "search_required": False,
        }

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_runs_controlled_multi_agent_workflow_and_archives_project(self):
        workflow = load_workflow_module()

        result = workflow.run_workflow(
            self.input_payload,
            runs_root=self.runs_root,
            projects_root=self.projects_root,
            created_at="2026-07-03T10:20:30+0800",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["mode"], "draft_only")
        self.assertFalse(result["safety"]["real_external_send"])
        self.assertEqual(result["model"], "deepseek/deepseek-v4-pro")

        run_dir = Path(result["workflow_run_dir"])
        project_dir = Path(result["project_dir"])
        self.assertTrue(run_dir.exists())
        self.assertTrue(project_dir.exists())
        self.assertTrue((run_dir / "input.json").exists())
        self.assertTrue((run_dir / "plan.json").exists())
        self.assertTrue((run_dir / "agent_tasks.json").exists())
        self.assertTrue((run_dir / "product_agent_output.json").exists())
        self.assertTrue((run_dir / "opportunity_agent_output.json").exists())
        self.assertTrue((run_dir / "content_agent_output.json").exists())
        self.assertTrue((run_dir / "social_agent_output.json").exists())
        self.assertTrue((run_dir / "factory_handoff_agent_output.json").exists())
        self.assertTrue((run_dir / "safety_agent_output.json").exists())
        self.assertTrue((run_dir / "archive_agent_output.json").exists())
        self.assertTrue((run_dir / "final_report.md").exists())
        self.assertTrue((run_dir / "trace.md").exists())
        self.assertTrue((project_dir / "report.md").exists())
        self.assertTrue((project_dir / "handoff.docx").exists())
        self.assertTrue((project_dir / "product_card.md").exists())
        self.assertTrue((self.projects_root / "index.html").exists())

        plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["external_action_mode"], "draft_only")
        self.assertGreaterEqual(len(plan["agents"]), 8)

        agent_tasks = json.loads((run_dir / "agent_tasks.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(agent_tasks), 8)
        self.assertIn("宇智能制造业获客总控 Agent", {item["agent_name"] for item in agent_tasks})

        final_report = (run_dir / "final_report.md").read_text(encoding="utf-8")
        self.assertIn("宇智能制造业获客工作流结果", final_report)
        self.assertIn("总控 Agent 任务拆解", final_report)
        self.assertIn("产品理解 Agent 输出", final_report)
        self.assertIn("商机发掘 Agent 输出", final_report)
        self.assertIn("宣传物料 Agent 输出", final_report)
        self.assertIn("社媒运营 Agent 输出", final_report)
        self.assertIn("工厂对接 Agent 输出", final_report)
        self.assertIn("风控审核 Agent 输出", final_report)
        self.assertIn("归档 Agent 输出", final_report)
        self.assertIn("draft_only", final_report)

        project_report = (project_dir / "report.md").read_text(encoding="utf-8")
        self.assertIn("总控 Agent 任务拆解", project_report)
        self.assertIn("draft_only", project_report)

    def test_accepts_named_test_case_wrapper_with_input_object(self):
        workflow = load_workflow_module()
        wrapped_payload = {
            "id": "wrapped-electronics",
            "name": "东莞电子连接件工厂多 Agent 获客工作流",
            "input": self.input_payload,
        }

        result = workflow.run_workflow(
            wrapped_payload,
            runs_root=self.runs_root,
            projects_root=self.projects_root,
            created_at="2026-07-03T10:21:30+0800",
        )

        self.assertTrue(result["ok"])
        self.assertIn("电子连接件", Path(result["project_dir"]).name)
        report_text = Path(result["report_path"]).read_text(encoding="utf-8")
        self.assertIn("电子连接件、线束、充电配件", report_text)


if __name__ == "__main__":
    unittest.main()
