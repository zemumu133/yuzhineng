import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(r"D:\OpenClaw")
SCRIPT = ROOT / "v2" / "scripts" / "create-pack1-portable-poc.py"


def load_pack1_module():
    spec = importlib.util.spec_from_file_location("create_pack1_portable_poc", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Pack1PortablePocTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pack1-portable-poc-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_builds_portable_package_without_runtime_data(self):
        pack1 = load_pack1_module()
        output = self.tmp / "yuzhineng-pack1-portable-poc"

        result = pack1.build_package(output, force=True)

        self.assertTrue(result["ok"])
        self.assertTrue((output / "PACKAGE_MANIFEST.json").exists())
        self.assertTrue((output / "README_安装_CN.md").exists())
        self.assertTrue((output / "tools" / "verify-pack1.ps1").exists())
        self.assertTrue((output / "tools" / "restore-agent-taxonomy.ps1").exists())
        self.assertTrue((output / "tools" / "start-yuzhineng-portable.ps1").exists())
        self.assertTrue((output / "tools" / "open-projects-index.ps1").exists())

        copied_root = output / "openclaw-v2" / "v2"
        self.assertTrue((copied_root / "config" / "agent_taxonomy.json").exists())
        self.assertTrue((copied_root / "scripts" / "repair_lobsterai_agent_taxonomy.ps1").exists())
        self.assertTrue((copied_root / "scripts" / "start-yuzhineng.ps1").exists())
        self.assertTrue((copied_root / "skills" / "domestic_signal_growth").exists())
        self.assertTrue((copied_root / "growth_os").exists())

        forbidden = [
            output / "openclaw-v2" / "secrets",
            output / "openclaw-v2" / "logs",
            output / "openclaw-v2" / "database",
            output / "openclaw-v2" / "backups",
            copied_root / "data",
            copied_root / "projects",
            copied_root / "runtimes",
            copied_root / "client-shell" / "lobsterai" / "src",
        ]
        for path in forbidden:
            self.assertFalse(path.exists(), str(path))

        manifest = json.loads((output / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest["real_external_send_enabled"])
        self.assertEqual(manifest["external_action_mode"], "draft_only_or_approval_required")

    def test_dry_run_reports_scope(self):
        pack1 = load_pack1_module()
        result = pack1.build_package(self.tmp / "dry-run-output", dry_run=True)

        self.assertTrue(result["ok"])
        self.assertTrue(result["dry_run"])
        self.assertGreater(result["selected_count"], 0)
