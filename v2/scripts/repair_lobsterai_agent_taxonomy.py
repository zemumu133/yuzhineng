from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\OpenClaw")
V2 = ROOT / "v2"
TAXONOMY_PATH = V2 / "config" / "agent_taxonomy.json"
DEFAULT_DB_PATH = Path(os.path.expandvars(r"%APPDATA%\LobsterAI\lobsterai.sqlite"))
DEFAULT_BACKUP_ROOT = ROOT / "backups" / "lobsterai-sqlite"
DEFAULT_MODEL = "deepseek/deepseek-v4-pro"
HIDDEN_FILE_AGENT_ID = "__yuzhineng_generated_file__"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def load_taxonomy(path: str | Path = TAXONOMY_PATH) -> dict[str, Any]:
    return read_json(Path(path))


def standard_agent_ids(taxonomy: dict[str, Any]) -> list[str]:
    return [str(agent["id"]) for agent in taxonomy.get("standard_agents", [])]


def deprecated_agent_map(taxonomy: dict[str, Any]) -> dict[str, str]:
    return {
        str(item["id"]): str(item["merge_to"])
        for item in taxonomy.get("deprecated_agents", [])
        if item.get("id") and item.get("merge_to")
    }


def backup_sqlite(db_path: Path, backup_root: Path = DEFAULT_BACKUP_ROOT) -> str:
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_path = backup_root / f"lobsterai-before-m1-1-agent-taxonomy-{time.strftime('%Y%m%d-%H%M%S')}.sqlite"
    source = sqlite3.connect(str(db_path))
    try:
        target = sqlite3.connect(str(backup_path))
        try:
            source.backup(target)
        finally:
            target.close()
    finally:
        source.close()
    return str(backup_path)


def now_ms() -> int:
    return int(time.time() * 1000)


def agent_prompt(agent: dict[str, Any]) -> str:
    return (
        f"你是{agent['name']}。你只处理宇智能本地制造业获客任务。"
        "所有发布、评论、私信、邮件、批量导出等外部动作只能生成草稿或审批项，"
        "不得真实外发，不得读取 secrets，不得伪造来源。"
    )


def ensure_ui_items_table(cur: sqlite3.Cursor) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS yuzhineng_ui_items (
          id TEXT PRIMARY KEY,
          item_type TEXT NOT NULL,
          owner_agent_id TEXT,
          project_id TEXT,
          file_type TEXT,
          display_area TEXT NOT NULL,
          source_table TEXT,
          source_id TEXT,
          title TEXT,
          path TEXT,
          created_at INTEGER,
          updated_at INTEGER
        )
        """
    )


def is_generated_file_title(title: str, taxonomy: dict[str, Any]) -> bool:
    value = (title or "").strip().lower()
    if not value:
        return False
    generated_names = {str(name).lower() for name in taxonomy.get("generated_file_names", [])}
    if value in generated_names:
        return True
    if value.startswith("成果文件") or value.startswith("归档文件"):
        return True
    suffixes = (".md", ".docx", ".json", ".xlsx", ".pdf", ".html")
    return value.endswith(suffixes) and len(value) <= 120


def file_type_from_title(title: str) -> str:
    value = (title or "").strip().lower()
    for suffix in (".docx", ".xlsx", ".pdf", ".html", ".json", ".md"):
        if value.endswith(suffix):
            return suffix.lstrip(".")
    return "file"


def upsert_standard_agent(cur: sqlite3.Cursor, agent: dict[str, Any], timestamp: int) -> None:
    cur.execute(
        """
        INSERT INTO agents (
          id, name, description, system_prompt, identity, model, working_directory,
          icon, skill_ids, enabled, pinned, pin_order, is_default, source, preset_id,
          created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0, ?, 0, 'custom', '', ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          name=excluded.name,
          description=excluded.description,
          system_prompt=excluded.system_prompt,
          identity=excluded.identity,
          model=excluded.model,
          working_directory=excluded.working_directory,
          icon=excluded.icon,
          skill_ids=excluded.skill_ids,
          enabled=1,
          pin_order=excluded.pin_order,
          updated_at=excluded.updated_at
        """,
        (
            agent["id"],
            agent["name"],
            agent.get("role", ""),
            agent_prompt(agent),
            agent.get("role", ""),
            DEFAULT_MODEL,
            str(V2 / "projects"),
            "agent-avatar-svg:lobster",
            json.dumps(agent.get("skills", []), ensure_ascii=False),
            int(agent.get("display_order", 999)),
            timestamp,
            timestamp,
        ),
    )


def disable_deprecated_agents(cur: sqlite3.Cursor, taxonomy: dict[str, Any], timestamp: int) -> dict[str, int]:
    moved_sessions = 0
    disabled_agents = 0
    for item in taxonomy.get("deprecated_agents", []):
        source_id = str(item.get("id") or "")
        target_id = str(item.get("merge_to") or "")
        if not source_id or not target_id:
            continue
        cur.execute("UPDATE cowork_sessions SET agent_id = ?, updated_at = ? WHERE agent_id = ?", (target_id, timestamp, source_id))
        moved_sessions += cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0
        cur.execute(
            """
            UPDATE agents
            SET enabled = 0,
                name = CASE WHEN name LIKE '[已合并]%' THEN name ELSE '[已合并] ' || name END,
                description = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (f"已合并到 {target_id}。保留历史配置，不在左侧 Agent 列表显示。", timestamp, source_id),
        )
        disabled_agents += cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0
    return {"moved_sessions": moved_sessions, "disabled_agents": disabled_agents}


def classify_generated_file_sessions(cur: sqlite3.Cursor, taxonomy: dict[str, Any], timestamp: int) -> int:
    rows = cur.execute("SELECT id, title, agent_id, created_at, updated_at FROM cowork_sessions").fetchall()
    moved = 0
    for session_id, title, agent_id, created_at, updated_at in rows:
        if not is_generated_file_title(str(title or ""), taxonomy):
            continue
        cur.execute(
            """
            INSERT OR REPLACE INTO yuzhineng_ui_items (
              id, item_type, owner_agent_id, project_id, file_type, display_area,
              source_table, source_id, title, path, created_at, updated_at
            )
            VALUES (?, 'file', ?, NULL, ?, 'project_workspace', 'cowork_sessions', ?, ?, NULL, ?, ?)
            """,
            (
                f"file-session-{session_id}",
                agent_id,
                file_type_from_title(str(title or "")),
                session_id,
                title,
                created_at or timestamp,
                timestamp,
            ),
        )
        cur.execute(
            "UPDATE cowork_sessions SET agent_id = ?, updated_at = ? WHERE id = ?",
            (HIDDEN_FILE_AGENT_ID, timestamp, session_id),
        )
        moved += 1
    return moved


def insert_agent_ui_items(cur: sqlite3.Cursor, taxonomy: dict[str, Any], timestamp: int) -> None:
    for agent in taxonomy.get("standard_agents", []):
        cur.execute(
            """
            INSERT OR REPLACE INTO yuzhineng_ui_items (
              id, item_type, owner_agent_id, project_id, file_type, display_area,
              source_table, source_id, title, path, created_at, updated_at
            )
            VALUES (?, 'agent', ?, NULL, NULL, 'sidebar', 'agents', ?, ?, NULL, ?, ?)
            """,
            (
                f"agent-{agent['id']}",
                agent["id"],
                agent["id"],
                agent["name"],
                timestamp,
                timestamp,
            ),
        )


def apply_agent_taxonomy(
    db_path: str | Path = DEFAULT_DB_PATH,
    *,
    taxonomy_path: str | Path = TAXONOMY_PATH,
    backup: bool = True,
    backup_root: str | Path = DEFAULT_BACKUP_ROOT,
) -> dict[str, Any]:
    db_path = Path(db_path)
    taxonomy = load_taxonomy(taxonomy_path)
    if not db_path.exists():
        return {"ok": False, "error": f"LobsterAI SQLite 不存在：{db_path}"}
    backup_path = backup_sqlite(db_path, Path(backup_root)) if backup else ""
    timestamp = now_ms()
    con = sqlite3.connect(str(db_path))
    try:
        cur = con.cursor()
        ensure_ui_items_table(cur)
        for agent in taxonomy.get("standard_agents", []):
            upsert_standard_agent(cur, agent, timestamp)
        migration = disable_deprecated_agents(cur, taxonomy, timestamp)
        file_sessions_moved = classify_generated_file_sessions(cur, taxonomy, timestamp)
        insert_agent_ui_items(cur, taxonomy, timestamp)
        visible_standard = cur.execute(
            """
            SELECT COUNT(*)
            FROM agents
            WHERE enabled = 1
              AND id IN ({})
            """.format(",".join("?" for _ in standard_agent_ids(taxonomy))),
            standard_agent_ids(taxonomy),
        ).fetchone()[0]
        active_deprecated = cur.execute(
            """
            SELECT COUNT(*)
            FROM agents
            WHERE enabled = 1
              AND id IN ({})
            """.format(",".join("?" for _ in deprecated_agent_map(taxonomy))),
            list(deprecated_agent_map(taxonomy).keys()),
        ).fetchone()[0]
        con.commit()
    finally:
        con.close()
    return {
        "ok": True,
        "db_path": str(db_path),
        "backup_path": backup_path,
        "standard_agent_count": len(standard_agent_ids(taxonomy)),
        "visible_standard_agent_count": visible_standard,
        "active_deprecated_agent_count": active_deprecated,
        "deprecated_agents_disabled": migration["disabled_agents"],
        "deprecated_sessions_moved": migration["moved_sessions"],
        "generated_file_sessions_moved": file_sessions_moved,
        "hidden_file_agent_id": HIDDEN_FILE_AGENT_ID,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="修复 LobsterAI 宇智能 Agent taxonomy 和侧边栏数据分层")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--taxonomy", default=str(TAXONOMY_PATH))
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--output-file", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = apply_agent_taxonomy(args.db_path, taxonomy_path=args.taxonomy, backup=not args.no_backup)
    if args.output_file:
        write_json(Path(args.output_file), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
