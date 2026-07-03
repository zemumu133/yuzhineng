from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from growth_os.action_intent.action_intent import ActionIntent, is_real_external_action


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


class SandboxExecutor:
    """Controlled local executor that never touches external platforms."""

    def __init__(self, allow_dev_sandbox_executor: bool = True) -> None:
        self.allow_dev_sandbox_executor = allow_dev_sandbox_executor

    def execute(self, action: ActionIntent) -> dict[str, Any]:
        if not self.allow_dev_sandbox_executor:
            return self._result(action, "blocked", "开发沙盒执行器未启用。")
        if action.mode not in {"draft_only", "approval_required"}:
            return self._result(action, "blocked", "Phase M1 不执行 advanced_auto_mode。")
        if is_real_external_action(action.action_type):
            return self._result(action, "blocked", "真实外部动作默认禁用，只允许进入审批队列。")
        return self._result(action, "simulated", "已在本地沙盒记录草稿动作，没有外发。")

    def _result(self, action: ActionIntent, status: str, message: str) -> dict[str, Any]:
        return {
            "execution_id": f"exec_{uuid4().hex[:16]}",
            "action_id": action.action_id,
            "project_id": action.project_id,
            "status": status,
            "dry_run": True,
            "external_effect": False,
            "message": message,
            "finished_at": now_iso(),
        }

