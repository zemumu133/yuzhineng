from __future__ import annotations

from typing import Any


def build_review_report(
    *,
    project_name: str,
    lead_count: int,
    action_count: int,
    approval_count: int,
    source_status: str,
    draft_only: bool,
    real_external_send: bool,
) -> str:
    return f"""# Growth OS 复盘报告

## 项目

- 项目名称：{project_name}
- 线索候选数量：{lead_count}
- ActionIntent 数量：{action_count}
- 审批项数量：{approval_count}
- 来源状态：{source_status}

## 安全结论

- 是否保持 draft_only：{'是' if draft_only else '否'}
- 是否发生真实外发：{'是' if real_external_send else '否'}
- 所有发布、评论、私信、邮件、加微信、群发动作均默认关闭，必须先进入人工审批。

## 下一步

1. 配置真实但合规的数据源，例如用户授权 CRM、人工 URL、企业名录 API。
2. 对高分线索做人工来源复核。
3. 只把审批通过的草稿交给人工在外部平台处理。
"""

