from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from growth_os.action_intent.action_intent import ActionIntent


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


@dataclass
class ApprovalItem:
    approval_id: str
    action_id: str
    project_id: str
    source_agent: str
    channel: str
    action_type: str
    target: str
    content: str | dict[str, Any]
    risk_level: str
    mode: str
    status: str = "pending"
    created_at: str = field(default_factory=now_iso)
    evidence_refs: list[str] = field(default_factory=list)
    reviewer_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def approval_from_action(action: ActionIntent) -> ApprovalItem:
    return ApprovalItem(
        approval_id=f"appr_{action.action_id.removeprefix('act_')}",
        action_id=action.action_id,
        project_id=action.project_id,
        source_agent=action.source_agent,
        channel=action.target_platform,
        action_type=action.action_type,
        target=action.target_entity,
        content=action.content,
        risk_level=action.risk_level,
        mode=action.mode,
        status="pending" if action.requires_approval else "not_required",
        evidence_refs=action.evidence_refs,
        reviewer_notes="本地审批项，不会自动发送或发布。",
    )


def build_approval_queue(actions: list[ActionIntent]) -> list[dict[str, Any]]:
    return [approval_from_action(action).to_dict() for action in actions if action.requires_approval]

