# Phase 2A：Search Provider 修复 + domestic_signal_growth Skill MVP 报告

## 1. 测试日期

- 测试时间：2026-07-02 12:30:40 +0800
- 最终测试目录：`D:\OpenClaw\v2\data\test-runs\phase2a-20260702-123040`

## 2. 当前分支

- 分支：`v2-open-source-growth-system`

## 3. 当前 commit 基线

- 基线 commit：`60440c40a1a5184408de8299767a87b1a432c025`

## 4. 修改文件清单

- `v2/skills/domestic_signal_growth/search_adapter.py`
- `v2/skills/domestic_signal_growth/domestic_signal_growth.py`
- `v2/skills/domestic_signal_growth/domestic_signal_growth.ps1`
- `v2/skills/domestic_signal_growth/hello_growth.ps1`
- `v2/skills/domestic_signal_growth/manifest.json`
- `v2/skills/domestic_signal_growth/README_CN.md`
- `v2/skills/domestic_signal_growth/examples/certificate_training.json`
- `v2/skills/domestic_signal_growth/examples/heavy_packaging.json`
- `v2/skills/domestic_signal_growth/examples/fitness_equipment.json`
- `v2/skills/domestic_signal_growth/tests/test_domestic_signal_growth.py`
- `v2/scripts/dev-autorun-gate.py`
- `v2/reports/DOMESTIC_SIGNAL_GROWTH_MVP_REPORT_CN.md`
- `v2/reports/PHASE_1A_GATE_RESULT_CN.md`

## 5. web-search provider 失败原因

- `web-search` bridge 服务本身可用，健康检查通过：`http://127.0.0.1:8923/api/health`。
- 直接使用旧 `.connection` 调 `/api/search` 返回 500，原因是缓存的 connection id 已失效，而 bridge 当前连接数为 0。
- Cowork/OpenClaw 侧的 `web_search` tool 仍显示 provider disabled 或 Gateway token mismatch 场景下不可用，这属于上层工具路由问题，不是本地 browser bridge 本身不可用。

## 6. web-search provider 修复结果

- 未大改 LobsterAI 上游源码。
- 新增 `search_adapter.py`，当连接失效时自动执行：
  1. `GET /api/health`
  2. `POST /api/browser/launch`
  3. `POST /api/browser/connect`
  4. `POST /api/search`
- 最终三轮任务均通过 `existing_lobster_web_search` 获取 5 条公开来源。

## 7. search_adapter 实现情况

- 支持 provider/mode：
  - `existing_lobster_web_search`
  - `browser_public_search`
  - `manual_seed_urls`
  - `no_source_available`
- 预留 `SEARXNG_BASE_URL=http://127.0.0.1:8080`，本阶段未安装 Docker / SearXNG。
- 没有真实来源时返回 `unverified` 或 `search_failed`，不伪造 URL。

## 8. domestic_signal_growth 输入格式

```json
{
  "product": "职业证书考评服务",
  "industry": "教育培训",
  "target_customers": ["培训机构", "人力资源公司"],
  "city": "全国",
  "platforms": ["小红书", "抖音"],
  "mode": "draft_only",
  "search_required": true
}
```

## 9. domestic_signal_growth 输出格式

- `source_status`
- `sources`
- `opportunity_judgement`
- `target_customer_types`
- `platform_strategy`
- `followup_drafts`
- `todos`
- `risk_notes`
- `next_steps`
- `search_trace`

## 10. 三个测试任务结果

| 任务 | Skill | DeepSeek V4 Pro | 来源状态 | 来源数 | draft_only | 行业适配 |
|---|---:|---:|---|---:|---:|---:|
| 职业证书考评服务 | 通过 | 通过 | verified_public_sources | 5 | 是 | 是 |
| 重型包装纸箱服务 | 通过 | 通过 | verified_public_sources | 5 | 是 | 是 |
| 健身器材 | 通过 | 通过 | verified_public_sources | 5 | 是 | 是 |

## 11. 每个任务是否有真实公开来源

- 三个任务均有公开 URL 来源。
- 来源完整保存在各任务的 `search_trace.json`。
- 示例目录：
  - `task-001-certificate\search_trace.json`
  - `task-002-carton\search_trace.json`
  - `task-003-fitness\search_trace.json`

## 12. 每个任务是否行业适配

- 职业证书考评服务：输出培训机构、人力资源公司、合规宣传边界、证书项目解释等内容。
- 重型包装纸箱服务：输出电商仓储、制造工厂、物流公司、破损率、承重、定制、交付等内容。
- 健身器材：输出健身房、经销商、跨境卖家、选型、空间、售后、素材本地化等内容。

## 13. 每个任务是否输出内容建议

- 三个任务均输出小红书和抖音内容建议。
- 包装和健身器材任务额外输出公众号策略。

## 14. 每个任务是否输出跟进话术

- 三个任务均输出公开评论草稿和私信草稿。
- 所有草稿均仅作 `draft_only`，不得自动外发。

## 15. 每个任务是否输出待办

- 三个任务均输出待办。
- 每条待办默认需要人工审批或人工确认。

## 16. DeepSeek V4 Pro 是否参与最终总结

- 已参与。
- OpenClaw CLI 实际使用：
  - provider：`deepseek`
  - model：`deepseek-v4-pro`
- token 用量：
  - 职业证书考评服务：约 18,614 tokens
  - 重型包装纸箱服务：约 19,096 tokens
  - 健身器材：约 18,755 tokens
- 注意：当前 Gateway 连接仍提示 token mismatch，OpenClaw 自动 fallback 到 embedded runner 后成功调用 DeepSeek。这不影响本阶段结果，但需要在后续修复 Gateway token 对齐。

## 17. 安全检查结果

- 不读取 secrets。
- 不提交 API Key、Token、Cookie、浏览器 Profile。
- 不真实发邮件。
- 不真实私信。
- 不真实评论。
- 不真实发帖。
- 不登录社媒。
- 所有外部动作均为 `draft_only`。
- 三个任务的 `safety_check.json` 均显示真实外发为 false。

## 18. 当前是否建议进入 Phase 2B：公开信号搜索增强

- 结论：A. MVP 成立，进入 Phase 2B：公开信号搜索增强。
- 进入 Phase 2B 的理由：
  - 搜索适配层可用。
  - Skill 已从占位升级为行业适配 MVP。
  - 三个业务任务均跑通。
  - DeepSeek V4 Pro 已参与总结。
  - 安全边界保持 draft_only。

## 19. 下一步建议

1. Phase 2B 增强公开搜索质量：关键词扩展、结果去重、来源相关性评分、广告/低质页面过滤。
2. 修复 OpenClaw Gateway token mismatch，让 CLI/UI 不再依赖 embedded fallback。
3. 将 `domestic_signal_growth` 接成更标准的 MCP/Skill 工具，让 Cowork UI 能自然调用。
4. 增加“来源可信度”和“是否适合触达”的评分字段。
5. 继续保持外部动作审批，不做自动私信、评论、发帖、邮件发送。

## 结论

A. MVP 成立，进入 Phase 2B：公开信号搜索增强。
