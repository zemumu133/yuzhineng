import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(r"D:\OpenClaw")
SCRIPT = ROOT / "v2" / "scripts" / "run_manufacturing_multi_agent_workflow.py"


def load_workflow_module():
    spec = importlib.util.spec_from_file_location("run_manufacturing_multi_agent_workflow_phase2f", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RealAgentCollaborationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="phase2f-real-agent-"))
        self.runs_root = self.tmp / "workflow-runs"
        self.collaboration_root = self.tmp / "multi-agent-runs"
        self.projects_root = self.tmp / "projects"
        self.input_payload = {
            "company_location": "东莞",
            "factory_type": "包装厂",
            "product_name": "重型包装纸箱、物流包装、出口包装",
            "product_description": "面向电商仓储、制造工厂、物流公司和外贸企业的重型包装纸箱和出口包装。",
            "factory_capabilities": ["重型纸箱定制", "出口包装打样", "物流包装加固"],
            "target_customer_hint": ["电商仓储", "制造工厂", "物流公司", "外贸企业"],
            "platforms": ["小红书", "抖音", "公众号"],
            "mode": "draft_only",
            "search_required": False,
        }

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_creates_real_agent_group_rework_and_workspace(self):
        workflow = load_workflow_module()

        result = workflow.run_workflow(
            self.input_payload,
            runs_root=self.runs_root,
            collaboration_root=self.collaboration_root,
            projects_root=self.projects_root,
            created_at="2026-07-03T12:10:30+0800",
            mirror_lobsterai_ui=False,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["mode"], "draft_only")
        self.assertEqual(result["model"], "deepseek/deepseek-v4-pro")
        self.assertFalse(result["safety"]["real_external_send"])

        collaboration = result["collaboration"]
        project_multi_dir = Path(collaboration["project_multi_agent_dir"])
        collaboration_run_dir = Path(collaboration["collaboration_run_dir"])
        self.assertTrue(project_multi_dir.exists())
        self.assertTrue(collaboration_run_dir.exists())

        required = [
            "run_manifest.json",
            "agent_tasks.json",
            "group_room_messages.json",
            "rework_log.json",
            "ui_trace.json",
            "agent_group_chat.html",
            "agent_workspace.html",
            "files/final_summary.md",
            "files/content_materials.md",
            "files/social_plan.md",
        ]
        for relative in required:
            self.assertTrue((project_multi_dir / relative).exists(), relative)

        agent_tasks = json.loads((project_multi_dir / "agent_tasks.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(agent_tasks), 9)
        task_agents = {item["agent_id"] for item in agent_tasks}
        self.assertIn("yuzhineng-product-analyst", task_agents)
        self.assertIn("yuzhineng-opportunity-researcher", task_agents)
        self.assertIn("yuzhineng-content-producer", task_agents)
        self.assertIn("yuzhineng-social-operator", task_agents)
        self.assertIn("yuzhineng-factory-handoff", task_agents)
        self.assertIn("yuzhineng-safety-reviewer", task_agents)
        self.assertIn("yuzhineng-summary-agent", task_agents)
        for task in agent_tasks:
            self.assertTrue(task["task_id"])
            self.assertEqual(task["status"], "completed")
            self.assertTrue(task["output_summary"])

        messages = json.loads((project_multi_dir / "group_room_messages.json").read_text(encoding="utf-8"))
        speakers = {item["sender_agent"] for item in messages}
        self.assertGreaterEqual(len(speakers), 6)
        self.assertTrue(any(item["message_type"] == "rework_required" for item in messages))
        self.assertTrue(any(item["message_type"] == "rework_done" for item in messages))

        rework = json.loads((project_multi_dir / "rework_log.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rework), 1)
        self.assertEqual(rework[0]["target_agent"], "yuzhineng-content-producer")
        self.assertEqual(rework[0]["fix_status"], "fixed")

        final_summary = (project_multi_dir / "files" / "final_summary.md").read_text(encoding="utf-8")
        self.assertIn("归纳 Agent 最终总结", final_summary)
        self.assertIn("draft_only", final_summary)

        group_html = (project_multi_dir / "agent_group_chat.html").read_text(encoding="utf-8")
        workspace_html = (project_multi_dir / "agent_workspace.html").read_text(encoding="utf-8")
        self.assertIn("Agent 工作群", group_html)
        self.assertIn("风控返工", group_html)
        self.assertIn("Agent 成果工作台", workspace_html)
        self.assertIn("产品理解 Agent", workspace_html)

        projects_index_html = (self.projects_root / "index.html").read_text(encoding="utf-8")
        self.assertIn("Agent 工作群", projects_index_html)
        self.assertIn("成果工作台", projects_index_html)
        self.assertIn("宣传物料", projects_index_html)

    def test_cli_defaults_do_not_mirror_lobsterai_ui(self):
        workflow = load_workflow_module()
        result = workflow.run_workflow(
            self.input_payload,
            runs_root=self.runs_root,
            collaboration_root=self.collaboration_root,
            projects_root=self.projects_root,
            created_at="2026-07-03T12:11:30+0800",
        )
        self.assertFalse(result["lobsterai_ui_mirror"]["ok"])
        self.assertEqual(result["lobsterai_ui_mirror"]["mirrored_sessions"], 0)


if __name__ == "__main__":
    unittest.main()
