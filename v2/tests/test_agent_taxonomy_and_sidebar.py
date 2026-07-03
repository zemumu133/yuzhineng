import importlib.util
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path


ROOT = Path(r"D:\OpenClaw")
V2 = ROOT / "v2"
SCRIPT = V2 / "scripts" / "repair_lobsterai_agent_taxonomy.py"


def load_repair_module():
    spec = importlib.util.spec_from_file_location("repair_lobsterai_agent_taxonomy_m1_1", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AgentTaxonomyAndSidebarTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="m1-1-agent-taxonomy-"))
        self.db_path = self.tmp / "lobsterai.sqlite"
        self._create_schema()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _create_schema(self):
        con = sqlite3.connect(str(self.db_path))
        try:
            con.execute(
                """
                CREATE TABLE agents (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    system_prompt TEXT,
                    identity TEXT,
                    model TEXT,
                    working_directory TEXT,
                    icon TEXT,
                    skill_ids TEXT,
                    enabled INTEGER,
                    pinned INTEGER,
                    pin_order INTEGER,
                    is_default INTEGER,
                    source TEXT,
                    preset_id TEXT,
                    created_at INTEGER,
                    updated_at INTEGER
                )
                """
            )
            con.execute(
                """
                CREATE TABLE cowork_sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    claude_session_id TEXT,
                    status TEXT,
                    pinned INTEGER,
                    pin_order INTEGER,
                    cwd TEXT,
                    system_prompt TEXT,
                    model_override TEXT,
                    execution_mode TEXT,
                    parent_session_id TEXT,
                    forked_from_message_id TEXT,
                    forked_at INTEGER,
                    fork_mode TEXT,
                    fork_workspace_path TEXT,
                    fork_git_branch TEXT,
                    fork_git_base_ref TEXT,
                    created_at INTEGER,
                    updated_at INTEGER,
                    active_skill_ids TEXT,
                    agent_id TEXT
                )
                """
            )
            now = 1000
            rows = [
                ("yuzhineng-lead-agent", "宇智能获客 Agent", 1),
                ("yuzhineng-content-agent", "宇智能内容 Agent", 1),
                ("yuzhineng-sales-agent", "宇智能销售 Agent", 1),
                ("yuzhineng-manufacturing-chief", "旧总控", 1),
            ]
            for agent_id, name, enabled in rows:
                con.execute(
                    """
                    INSERT INTO agents (
                      id, name, description, system_prompt, identity, model, working_directory,
                      icon, skill_ids, enabled, pinned, pin_order, is_default, source, preset_id,
                      created_at, updated_at
                    )
                    VALUES (?, ?, '', '', '', 'deepseek/deepseek-v4-pro', '', '', '[]', ?, 0, NULL, 0, 'custom', '', ?, ?)
                    """,
                    (agent_id, name, enabled, now, now),
                )
            con.execute(
                """
                INSERT INTO cowork_sessions (
                  id, title, status, pinned, pin_order, cwd, system_prompt, model_override,
                  execution_mode, fork_mode, created_at, updated_at, active_skill_ids, agent_id
                )
                VALUES ('session-lead', '旧获客任务', 'completed', 0, NULL, '', '', '', 'local', 'none', ?, ?, '[]', 'yuzhineng-lead-agent')
                """,
                (now, now),
            )
            con.execute(
                """
                INSERT INTO cowork_sessions (
                  id, title, status, pinned, pin_order, cwd, system_prompt, model_override,
                  execution_mode, fork_mode, created_at, updated_at, active_skill_ids, agent_id
                )
                VALUES ('session-file', 'report.md', 'completed', 0, NULL, '', '', '', 'local', 'none', ?, ?, '[]', 'yuzhineng-content-agent')
                """,
                (now, now),
            )
            con.commit()
        finally:
            con.close()

    def test_taxonomy_contains_unique_standard_agents(self):
        taxonomy = json.loads((V2 / "config" / "agent_taxonomy.json").read_text(encoding="utf-8"))
        ids = [agent["id"] for agent in taxonomy["standard_agents"]]

        self.assertEqual(len(ids), 9)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("yuzhineng-manufacturing-chief", ids)
        chief = next(agent for agent in taxonomy["standard_agents"] if agent["id"] == "yuzhineng-manufacturing-chief")
        self.assertIn("manufacturing_multi_agent_workflow", chief["skills"])

    def test_repair_merges_duplicates_and_moves_generated_files_out_of_sidebar(self):
        repair = load_repair_module()

        result = repair.apply_agent_taxonomy(self.db_path, backup=False)

        self.assertTrue(result["ok"])
        self.assertEqual(result["standard_agent_count"], 9)
        self.assertEqual(result["visible_standard_agent_count"], 9)
        self.assertEqual(result["active_deprecated_agent_count"], 0)
        self.assertGreaterEqual(result["deprecated_sessions_moved"], 1)
        self.assertEqual(result["generated_file_sessions_moved"], 1)

        con = sqlite3.connect(str(self.db_path))
        try:
            active_deprecated = con.execute(
                """
                SELECT COUNT(*)
                FROM agents
                WHERE enabled = 1
                  AND id IN ('yuzhineng-lead-agent', 'yuzhineng-content-agent', 'yuzhineng-sales-agent')
                """
            ).fetchone()[0]
            lead_session_agent = con.execute("SELECT agent_id FROM cowork_sessions WHERE id = 'session-lead'").fetchone()[0]
            file_session_agent = con.execute("SELECT agent_id FROM cowork_sessions WHERE id = 'session-file'").fetchone()[0]
            chief_skills = con.execute("SELECT skill_ids FROM agents WHERE id = 'yuzhineng-manufacturing-chief'").fetchone()[0]
            file_item = con.execute(
                """
                SELECT item_type, display_area, file_type
                FROM yuzhineng_ui_items
                WHERE source_id = 'session-file'
                """
            ).fetchone()
        finally:
            con.close()

        self.assertEqual(active_deprecated, 0)
        self.assertEqual(lead_session_agent, "yuzhineng-opportunity-researcher")
        self.assertEqual(file_session_agent, repair.HIDDEN_FILE_AGENT_ID)
        self.assertIn("manufacturing_multi_agent_workflow", json.loads(chief_skills))
        self.assertEqual(file_item, ("file", "project_workspace", "md"))


if __name__ == "__main__":
    unittest.main()
