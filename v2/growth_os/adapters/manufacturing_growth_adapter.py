from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from growth_os.action_intent.action_intent import ActionIntent, action_intent_from_output, create_action_intent
from growth_os.approval_queue.approval_queue import build_approval_queue
from growth_os.audit_log.audit_log import AuditLog
from growth_os.content_factory.content_factory import build_content_drafts
from growth_os.lead_research.lead_research import build_lead_research
from growth_os.private_domain_sop.private_domain_sop import build_private_domain_sop
from growth_os.review_report.review_report import build_review_report
from growth_os.sandbox_executor.sandbox_executor import SandboxExecutor


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_sources(opportunity_output: dict[str, Any]) -> list[dict[str, Any]]:
    sources = opportunity_output.get("sources") or opportunity_output.get("public_sources") or []
    normalized: list[dict[str, Any]] = []
    for source in _as_list(sources):
        if not isinstance(source, dict):
            continue
        url = source.get("url") or source.get("source_url") or ""
        title = source.get("title") or source.get("source_title") or "公开来源"
        excerpt = source.get("snippet") or source.get("source_excerpt") or source.get("excerpt") or ""
        normalized.append({"url": url or "unknown", "title": title, "excerpt": excerpt})
    return normalized


def _profile_from_product_output(product_output: dict[str, Any], input_data: dict[str, Any]) -> dict[str, Any]:
    profile = dict(product_output.get("product_profile") or {})
    profile.setdefault("product_name", input_data.get("product_name") or input_data.get("product") or "制造业产品")
    profile.setdefault("factory_type", input_data.get("factory_type") or input_data.get("industry") or "制造业工厂")
    profile.setdefault("location", input_data.get("company_location") or "东莞")
    profile.setdefault("target_customers", input_data.get("target_customer_hint") or input_data.get("target_customers") or [])
    profile.setdefault("mode", "draft_only")
    return profile


def _target_customers(input_data: dict[str, Any], product_profile: dict[str, Any]) -> list[str]:
    values = input_data.get("target_customer_hint") or input_data.get("target_customers") or product_profile.get("target_customers") or []
    return [str(item).strip() for item in _as_list(values) if str(item).strip()]


def _intent_for_items(
    *,
    project_id: str,
    source_agent: str,
    output_type: str,
    items: list[Any],
    evidence_refs: list[str],
) -> list[ActionIntent]:
    actions: list[ActionIntent] = []
    for index, item in enumerate(items, start=1):
        title = item.get("title") if isinstance(item, dict) else f"{output_type}-{index}"
        actions.append(
            action_intent_from_output(
                project_id=project_id,
                source_agent=source_agent,
                output_type=output_type,
                title=str(title or f"{output_type}-{index}"),
                body=item,
                evidence_refs=evidence_refs,
            )
        )
    return actions


def build_action_intents(
    *,
    project_id: str,
    content_drafts: dict[str, Any],
    private_sop: dict[str, Any],
    leads: list[dict[str, Any]],
    evidence_refs: list[str],
) -> list[ActionIntent]:
    actions: list[ActionIntent] = []
    actions.extend(
        _intent_for_items(
            project_id=project_id,
            source_agent="yuzhineng-content-producer",
            output_type="xiaohongshu_note",
            items=_as_list(content_drafts.get("xiaohongshu_notes")),
            evidence_refs=evidence_refs,
        )
    )
    actions.extend(
        _intent_for_items(
            project_id=project_id,
            source_agent="yuzhineng-content-producer",
            output_type="douyin_script",
            items=_as_list(content_drafts.get("douyin_scripts")),
            evidence_refs=evidence_refs,
        )
    )
    actions.extend(
        _intent_for_items(
            project_id=project_id,
            source_agent="yuzhineng-social-operator",
            output_type="comment_reply",
            items=_as_list(private_sop.get("comment_reply_drafts")),
            evidence_refs=evidence_refs,
        )
    )
    actions.extend(
        _intent_for_items(
            project_id=project_id,
            source_agent="yuzhineng-social-operator",
            output_type="dm",
            items=_as_list(private_sop.get("dm_drafts")),
            evidence_refs=evidence_refs,
        )
    )
    actions.append(
        action_intent_from_output(
            project_id=project_id,
            source_agent="yuzhineng-factory-handoff",
            output_type="factory_handoff",
            title="工厂销售交接单",
            body={"lead_count": len(leads), "mode": "draft_only"},
            evidence_refs=evidence_refs,
        )
    )
    actions.append(
        create_action_intent(
            project_id=project_id,
            source_agent="yuzhineng-factory-handoff",
            action_type="export_lead_list",
            target_platform="internal",
            target_entity="lead_candidates.json",
            content={"lead_count": len(leads), "file": "lead_candidates.json"},
            mode="draft_only",
            evidence_refs=evidence_refs,
            safety_notes=["线索列表仅保存到本地项目归档，批量导出真实客户数据需单独审批。"],
        )
    )
    return actions


def build_growth_os_workspace(
    *,
    project_dir: str | Path,
    run_dir: str | Path | None,
    input_data: dict[str, Any],
    product_output: dict[str, Any],
    opportunity_output: dict[str, Any],
    project_id: str,
    project_name: str,
) -> dict[str, Any]:
    project_path = Path(project_dir)
    run_path = Path(run_dir) if run_dir else None
    product_profile = _profile_from_product_output(product_output, input_data)
    public_sources = _normalize_sources(opportunity_output)
    target_customers = _target_customers(input_data, product_profile)
    lead_research = build_lead_research(
        product_profile=product_profile,
        target_customers=target_customers,
        public_sources=public_sources,
        location=str(product_profile.get("location") or "东莞"),
    )
    content_drafts = build_content_drafts(product_profile, lead_research)
    private_sop = build_private_domain_sop(product_profile, lead_research)
    evidence_refs = [item["evidence_id"] for item in lead_research["evidence"]]
    actions = build_action_intents(
        project_id=project_id,
        content_drafts=content_drafts,
        private_sop=private_sop,
        leads=lead_research["lead_candidates"],
        evidence_refs=evidence_refs,
    )
    approval_queue = build_approval_queue(actions)

    audit = AuditLog()
    audit.record(project_id=project_id, actor="growth_os_adapter", event="growth_os.workspace.created", payload={"project_name": project_name})
    sandbox = SandboxExecutor(allow_dev_sandbox_executor=True)
    sandbox_results = [sandbox.execute(action) for action in actions]
    for action, result in zip(actions, sandbox_results):
        audit.record(project_id=project_id, actor=action.source_agent, event="action_intent.sandbox_checked", payload=result)

    review_report = build_review_report(
        project_name=project_name,
        lead_count=len(lead_research["lead_candidates"]),
        action_count=len(actions),
        approval_count=len(approval_queue),
        source_status=lead_research["source_status"],
        draft_only=True,
        real_external_send=False,
    )

    action_dicts = [action.to_dict() for action in actions]
    files = {
        "product_profile": project_path / "product_profile.json",
        "sources": project_path / "sources.json",
        "lead_candidates": project_path / "lead_candidates.json",
        "leads": project_path / "leads.json",
        "evidence": project_path / "evidence.json",
        "content_drafts": project_path / "content_drafts.json",
        "private_domain_sop": project_path / "private_domain_sop.json",
        "action_intents": project_path / "action_intents.json",
        "approval_queue": project_path / "approval_queue.json",
        "sandbox_results": project_path / "sandbox_results.json",
        "audit_log": project_path / "audit_log.json",
        "review_report": project_path / "review_report.md",
    }
    write_json(files["product_profile"], product_profile)
    write_json(files["sources"], public_sources)
    write_json(files["lead_candidates"], lead_research["lead_candidates"])
    write_json(files["leads"], lead_research["lead_candidates"])
    write_json(files["evidence"], lead_research["evidence"])
    write_json(files["content_drafts"], content_drafts)
    write_json(files["private_domain_sop"], private_sop)
    write_json(files["action_intents"], action_dicts)
    write_json(files["approval_queue"], approval_queue)
    write_json(files["sandbox_results"], sandbox_results)
    write_json(files["audit_log"], audit.to_list())
    write_text(files["review_report"], review_report)

    manifest_path = project_path / "project_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        manifest["growth_os"] = {
            "enabled": True,
            "lead_count": len(lead_research["lead_candidates"]),
            "action_intent_count": len(action_dicts),
            "approval_queue_count": len(approval_queue),
            "draft_only": True,
            "real_external_send": False,
            "generated_files": {key: str(path) for key, path in files.items()},
        }
        write_json(manifest_path, manifest)

    if run_path:
        write_json(run_path / "growth_os_workspace.json", {"project_dir": str(project_path), "files": {k: str(v) for k, v in files.items()}})
        write_json(run_path / "action_intents.json", action_dicts)
        write_json(run_path / "approval_queue.json", approval_queue)
        write_text(run_path / "review_report.md", review_report)

    return {
        "ok": True,
        "project_id": project_id,
        "project_dir": str(project_path),
        "source_status": lead_research["source_status"],
        "lead_count": len(lead_research["lead_candidates"]),
        "action_intent_count": len(action_dicts),
        "approval_queue_count": len(approval_queue),
        "draft_only": True,
        "real_external_send": False,
        "files": {key: str(path) for key, path in files.items()},
    }
