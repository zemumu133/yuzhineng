from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
from uuid import uuid4


ACTION_TYPES = {
    "create_content_draft",
    "create_social_post_draft",
    "create_comment_reply_draft",
    "create_dm_draft",
    "create_email_draft",
    "create_call_script",
    "create_factory_handoff",
    "export_lead_list",
    "publish_social_post",
    "send_comment",
    "send_dm",
    "send_email",
    "add_wechat_contact",
    "group_message",
    "delete_data",
}

MODES = {"draft_only", "approval_required", "advanced_auto_mode"}
APPROVAL_STATUSES = {"pending", "approved", "rejected", "needs_revision", "manual_done", "not_required"}

REAL_EXTERNAL_ACTION_TYPES = {
    "publish_social_post",
    "send_comment",
    "send_dm",
    "send_email",
    "add_wechat_contact",
    "group_message",
}

HIGH_RISK_ACTION_TYPES = REAL_EXTERNAL_ACTION_TYPES | {"export_lead_list", "delete_data"}
DRAFT_ACTION_TYPES = ACTION_TYPES - REAL_EXTERNAL_ACTION_TYPES
DEFAULT_DISABLED_ACTION_TYPES = REAL_EXTERNAL_ACTION_TYPES


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def stable_action_id(parts: dict[str, Any] | None = None) -> str:
    if not parts:
        return f"act_{uuid4().hex}"
    raw = repr(sorted(parts.items())).encode("utf-8")
    return "act_" + sha256(raw).hexdigest()[:20]


def is_real_external_action(action_type: str) -> bool:
    return action_type in REAL_EXTERNAL_ACTION_TYPES


def default_risk_level(action_type: str) -> str:
    if action_type in {"add_wechat_contact", "group_message", "delete_data"}:
        return "high"
    if action_type in HIGH_RISK_ACTION_TYPES:
        return "medium"
    return "low"


def default_requires_approval(action_type: str, mode: str) -> bool:
    if action_type in HIGH_RISK_ACTION_TYPES:
        return True
    if mode in {"approval_required", "advanced_auto_mode"}:
        return True
    return False


@dataclass
class ActionIntent:
    action_id: str
    project_id: str
    source_agent: str
    action_type: str
    target_platform: str
    target_entity: str
    content: str | dict[str, Any]
    risk_level: str
    mode: str = "draft_only"
    requires_approval: bool = True
    approval_status: str = "pending"
    created_at: str = field(default_factory=utc_now_iso)
    evidence_refs: list[str] = field(default_factory=list)
    safety_notes: list[str] = field(default_factory=list)
    disabled_by_default: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_action_intent(action: ActionIntent) -> None:
    if action.action_type not in ACTION_TYPES:
        raise ValueError(f"Unsupported action_type: {action.action_type}")
    if action.mode not in MODES:
        raise ValueError(f"Unsupported mode: {action.mode}")
    if action.approval_status not in APPROVAL_STATUSES:
        raise ValueError(f"Unsupported approval_status: {action.approval_status}")
    if not action.project_id:
        raise ValueError("project_id is required")
    if not action.source_agent:
        raise ValueError("source_agent is required")
    if action.action_type in DEFAULT_DISABLED_ACTION_TYPES and action.mode != "draft_only":
        action.requires_approval = True
        action.disabled_by_default = True


def create_action_intent(
    *,
    project_id: str,
    source_agent: str,
    action_type: str,
    target_platform: str = "internal",
    target_entity: str = "project",
    content: str | dict[str, Any] = "",
    mode: str = "draft_only",
    evidence_refs: list[str] | None = None,
    safety_notes: list[str] | None = None,
    risk_level: str | None = None,
    action_id: str | None = None,
) -> ActionIntent:
    if action_type not in ACTION_TYPES:
        raise ValueError(f"Unsupported action_type: {action_type}")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    real_external = is_real_external_action(action_type)
    disabled_by_default = action_type in DEFAULT_DISABLED_ACTION_TYPES
    final_risk = risk_level or default_risk_level(action_type)
    requires_approval = default_requires_approval(action_type, mode)
    if real_external:
        requires_approval = True
        if mode == "advanced_auto_mode":
            safety_notes = [
                *(safety_notes or []),
                "真实外部动作默认禁用；高级自动模式也必须先经过人工审批和功能开关。",
            ]

    approval_status = "pending" if requires_approval else "not_required"
    action = ActionIntent(
        action_id=action_id
        or stable_action_id(
            {
                "project_id": project_id,
                "source_agent": source_agent,
                "action_type": action_type,
                "target_platform": target_platform,
                "target_entity": target_entity,
                "content": repr(content)[:200],
            }
        ),
        project_id=project_id,
        source_agent=source_agent,
        action_type=action_type,
        target_platform=target_platform,
        target_entity=target_entity,
        content=content,
        risk_level=final_risk,
        mode=mode,
        requires_approval=requires_approval,
        approval_status=approval_status,
        evidence_refs=evidence_refs or [],
        safety_notes=safety_notes or [],
        disabled_by_default=disabled_by_default,
    )
    validate_action_intent(action)
    return action


def action_intent_from_output(
    *,
    project_id: str,
    source_agent: str,
    output_type: str,
    title: str,
    body: Any,
    evidence_refs: list[str] | None = None,
) -> ActionIntent:
    mapping = {
        "xiaohongshu_note": ("create_social_post_draft", "xiaohongshu"),
        "douyin_script": ("create_content_draft", "douyin"),
        "wechat_article": ("create_social_post_draft", "wechat"),
        "comment_reply": ("create_comment_reply_draft", "comment_area"),
        "dm": ("create_dm_draft", "private_message"),
        "email": ("create_email_draft", "email"),
        "call_script": ("create_call_script", "phone"),
        "factory_handoff": ("create_factory_handoff", "internal"),
        "lead_export": ("export_lead_list", "internal"),
    }
    action_type, platform = mapping.get(output_type, ("create_content_draft", "internal"))
    return create_action_intent(
        project_id=project_id,
        source_agent=source_agent,
        action_type=action_type,
        target_platform=platform,
        target_entity=title,
        content=body,
        mode="draft_only",
        evidence_refs=evidence_refs or [],
        safety_notes=["本动作仅生成草稿或内部交接材料，不真实外发。"],
    )

