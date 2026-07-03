import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(r"D:\OpenClaw")
V2 = ROOT / "v2"
sys.path.insert(0, str(V2))


def load_workflow_module():
    script = V2 / "scripts" / "run_manufacturing_multi_agent_workflow.py"
    spec = importlib.util.spec_from_file_location("m1_run_manufacturing_multi_agent_workflow", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GrowthOSMergeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="m1-growth-os-merge-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_action_intent_defaults_block_external_actions(self):
        from growth_os.action_intent.action_intent import create_action_intent

        action = create_action_intent(
            project_id="proj_test",
            source_agent="yuzhineng-social-operator",
            action_type="send_dm",
            target_platform="xiaohongshu",
            target_entity="潜在线索",
            content="私信草稿",
            mode="draft_only",
        )

        self.assertTrue(action.requires_approval)
        self.assertEqual(action.approval_status, "pending")
        self.assertTrue(action.disabled_by_default)
        self.assertEqual(action.mode, "draft_only")

    def test_feature_flags_example_keeps_sensitive_features_off(self):
        flags = json.loads((V2 / "config" / "feature_flags.example.json").read_text(encoding="utf-8"))
        self.assertEqual(flags["external_actions_default"], "draft_only")
        self.assertFalse(flags["enable_real_publish"])
        self.assertFalse(flags["enable_auto_comment"])
        self.assertFalse(flags["enable_auto_dm"])
        self.assertFalse(flags["enable_auto_email"])
        self.assertFalse(flags["enable_add_wechat_contact"])
        self.assertFalse(flags["enable_group_message"])
        self.assertFalse(flags["enable_batch_export"])
        self.assertFalse(flags["enable_platform_login"])
        self.assertFalse(flags["enable_advanced_auto_mode"])
        self.assertTrue(flags["require_human_approval_for_external_actions"])
        self.assertTrue(flags["audit_all_actions"])
        self.assertTrue(flags["allow_dev_sandbox_executor"])

    def test_data_acquisition_layer_creates_evidence_backed_leads(self):
        from growth_os.data_acquisition.connectors import build_manual_url_evidence, build_sandbox_company_leads

        evidence = build_manual_url_evidence(
            [{"url": "https://example.com/public", "title": "公开来源", "excerpt": "摘要"}]
        )
        leads = build_sandbox_company_leads(
            product_name="重型包装纸箱",
            target_customers=["电商仓储", "制造工厂"],
            evidence_items=evidence,
        )

        self.assertEqual(len(evidence), 1)
        self.assertEqual(len(leads), 2)
        self.assertEqual(leads[0]["contact_status"], "unknown")
        self.assertTrue(leads[0]["source_refs"])

    def test_manufacturing_workflow_writes_growth_os_archive_files(self):
        workflow = load_workflow_module()
        case = json.loads(
            (V2 / "test-cases" / "growth_os_merge" / "dongguan_heavy_packaging_growth_os.json").read_text(
                encoding="utf-8"
            )
        )

        result = workflow.run_workflow(
            case,
            runs_root=self.tmp / "workflow-runs",
            collaboration_root=self.tmp / "multi-agent-runs",
            projects_root=self.tmp / "projects",
            created_at="2026-07-03T14:10:00+0800",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["mode"], "draft_only")
        self.assertIn("growth_os", result)
        growth_os = result["growth_os"]
        self.assertTrue(growth_os["ok"])
        self.assertTrue(growth_os["draft_only"])
        self.assertFalse(growth_os["real_external_send"])
        self.assertGreaterEqual(growth_os["lead_count"], 1)
        self.assertGreaterEqual(growth_os["action_intent_count"], 1)
        self.assertGreaterEqual(growth_os["approval_queue_count"], 1)

        project_dir = Path(result["project_dir"])
        required = [
            "product_profile.json",
            "sources.json",
            "lead_candidates.json",
            "evidence.json",
            "action_intents.json",
            "approval_queue.json",
            "report.md",
            "handoff.docx",
            "review_report.md",
        ]
        for file_name in required:
            self.assertTrue((project_dir / file_name).exists(), file_name)

        actions = json.loads((project_dir / "action_intents.json").read_text(encoding="utf-8"))
        approvals = json.loads((project_dir / "approval_queue.json").read_text(encoding="utf-8"))
        self.assertTrue(all(item["mode"] in {"draft_only", "approval_required"} for item in actions))
        self.assertTrue(all(item["status"] in {"pending", "not_required"} for item in approvals))


if __name__ == "__main__":
    unittest.main()
