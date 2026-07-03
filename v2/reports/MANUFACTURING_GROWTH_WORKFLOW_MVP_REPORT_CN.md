# Phase 2B：东莞制造业获客工作流产品化 MVP 报告

## 1. 测试日期

- 日期：2026-07-02
- 分支：v2-open-source-growth-system
- 项目名称：宇智能

## 2. 本阶段目标

把 `domestic_signal_growth` 从通用获客占位能力，升级为面向东莞制造业企业的产品化工作流 MVP。

核心场景：

- 产品资料理解
- 商机发掘
- 宣传物料生成
- 社媒发布计划
- 评论/私信草稿
- 账号养成
- 工厂销售交接单
- 人工待办和风险提示

所有外部动作保持 `draft_only`，未真实发布、评论、私信或发邮件。

## 3. 修改文件清单

- `D:\OpenClaw\v2\V2_FINAL_GOAL_CN.md`
- `D:\OpenClaw\v2\V2_PRODUCT_DIRECTION_CN.md`
- `D:\OpenClaw\v2\config\yuzhineng-product-mode.example.json`
- `D:\OpenClaw\v2\dev-config\dev-auto-run.example.json`
- `D:\OpenClaw\v2\scripts\dev-autorun-gate.py`
- `D:\OpenClaw\v2\skills\domestic_signal_growth\domestic_signal_growth.py`
- `D:\OpenClaw\v2\skills\domestic_signal_growth\tests\test_domestic_signal_growth.py`
- `D:\OpenClaw\v2\workflows\dongguan_manufacturing_growth\workflow.json`
- `D:\OpenClaw\v2\workflows\dongguan_manufacturing_growth\README_CN.md`
- `D:\OpenClaw\v2\workflows\dongguan_manufacturing_growth\steps_CN.md`
- `D:\OpenClaw\v2\workflows\dongguan_manufacturing_growth\acceptance_CN.md`
- `D:\OpenClaw\v2\workflows\dongguan_manufacturing_growth\examples\heavy_packaging.json`
- `D:\OpenClaw\v2\workflows\dongguan_manufacturing_growth\examples\fitness_equipment.json`
- `D:\OpenClaw\v2\workflows\dongguan_manufacturing_growth\examples\electronics_parts.json`
- `D:\OpenClaw\v2\test-cases\manufacturing_growth\heavy_packaging.json`
- `D:\OpenClaw\v2\test-cases\manufacturing_growth\fitness_equipment.json`
- `D:\OpenClaw\v2\test-cases\manufacturing_growth\electronics_parts.json`

## 4. 新增工作流

目录：

`D:\OpenClaw\v2\workflows\dongguan_manufacturing_growth\`

工作流 ID：

`dongguan_manufacturing_growth`

默认模式：

`draft_only`

默认模型配置：

`deepseek/deepseek-v4-pro`

本阶段预置 6 个制造业 Agent：

- 宇智能制造业获客总控 Agent
- 产品理解 Agent
- 商机发掘 Agent
- 宣传物料 Agent
- 社媒运营 Agent
- 工厂对接 Agent

## 5. Skill 实现结果

`domestic_signal_growth` 已新增制造业字段：

- `product_understanding`
- `opportunity_discovery`
- `target_customer_segments`
- `public_sources`
- `content_materials`
- `social_publish_plan`
- `comment_reply_drafts`
- `dm_drafts`
- `account_nurturing_plan`
- `factory_handoff_sheet`
- `todos`
- `risk_notes`
- `next_steps`

修复过的关键问题：

- 制造业输入未传 `industry` 时，不再继承默认“教育培训”，而是使用 `factory_type`。
- 电子配件厂不再被“跨境/器材”等宽泛关键词误判为健身器材模板。
- 模板匹配顺序已调整为：电子配件、包装、健身器材、证书培训、通用模板。

## 6. Dev Auto-Run 结果

执行命令：

```powershell
$env:YUZHINENG_DEV_AUTO_RUN='1'
python D:\OpenClaw\v2\scripts\dev-autorun-gate.py --run-phase2b
```

最新执行：

- Run ID：`phase2b-20260702-171315`
- 结果目录：`D:\OpenClaw\v2\data\test-runs\phase2b-20260702-171315`
- 用例数：3
- 三个用例均生成完整 Skill 输出：是
- 三个用例均保持 `draft_only`：是
- 三个用例均生成工厂销售交接单：是

用例：

- 东莞重型包装纸箱厂
- 东莞健身器材厂
- 东莞电子配件厂

说明：

Phase 2B 的 Dev Auto-Run 默认跳过 OpenClaw agent 模型汇总，配置项为：

`phase2b_enable_openclaw_model_validation=false`

原因是本轮实测中 OpenClaw agent CLI 在自动汇总阶段可能长时间不返回。为避免阻塞产品化验证，Phase 2B 以可复现的 Skill 输出和 UI 实测作为 MVP 验收依据。DeepSeek V4 Pro 在桌面 UI 路径中仍被真实使用。

## 7. 桌面 UI 鼠标验证

用户要求使用 Computer Use 插件进行真实鼠标验证。当前工具环境没有可用的 Computer Use 插件，因此本轮使用 Windows 本机鼠标/键盘自动化替代，真实点击 LobsterAI 桌面 UI。

验证任务：

“我要推广东莞电子连接件工厂，目标客户是电子厂、品牌商、跨境卖家和维修渠道。请生成产品理解、商机发掘、小红书内容、抖音脚本、评论回复草稿、私信草稿、账号养成计划和工厂销售交接单。不要真实发布、不要私信、不要评论、不要发邮件。”

UI 结果：

- 输入框可真实点击：是
- 文本可真实粘贴：是
- 发送按钮可真实点击：是
- 模型显示为 `DeepSeek V4 Pro`：是
- 触发 web-search：是
- 触发 web_fetch：是
- 触发 docx 技能：是
- 生成 Markdown 推广方案：是
- 生成 Word 销售交接单：是
- 真实外发：否
- 社媒登录：否
- 读取 secrets：否

生成文件：

- `C:\Users\Admin\AppData\Roaming\LobsterAI\openclaw\state\workspace-yuzhineng-content-agent\东莞电子连接件工厂推广方案.md`
- `C:\Users\Admin\AppData\Roaming\LobsterAI\openclaw\state\workspace-yuzhineng-content-agent\工厂销售客户交接单.docx`

截图证据：

- `D:\OpenClaw\v2\reports\assets\manufacturing-growth-ui\ui-phase2b-mouse3-after-90s.png`
- `D:\OpenClaw\v2\reports\assets\manufacturing-growth-ui\ui-phase2b-mouse3-after-210s.png`
- `D:\OpenClaw\v2\reports\assets\manufacturing-growth-ui\ui-phase2b-mouse3-after-390s.png`
- `D:\OpenClaw\v2\reports\assets\manufacturing-growth-ui\ui-phase2b-mouse3-after-510s.png`

UI 轨迹：

- `D:\OpenClaw\v2\data\ui-runs\manufacturing-growth\phase2b-ui-mouse-003.json`
- `D:\OpenClaw\v2\data\ui-runs\manufacturing-growth\phase2b-ui-mouse-003-wait-docx.json`

## 8. 测试结果

单元测试：

```powershell
python -m unittest discover -s D:\OpenClaw\v2\skills\domestic_signal_growth\tests -v
```

结果：

- 5 个测试全部通过。

语法检查：

```powershell
python -m py_compile D:\OpenClaw\v2\skills\domestic_signal_growth\domestic_signal_growth.py D:\OpenClaw\v2\skills\domestic_signal_growth\search_adapter.py D:\OpenClaw\v2\scripts\dev-autorun-gate.py
```

结果：

- 通过。

Skill 直跑：

- 包装厂：通过，能生成产品理解、商机、内容、交接单。
- 健身器材厂：通过，能生成产品理解、商机、内容、交接单。
- 电子配件厂：通过，且不再串到健身模板。

## 9. 安全检查

- 未读取 `D:\OpenClaw\secrets`。
- 未提交 API Key、Token、Cookie、浏览器 Profile。
- 未真实发送邮件。
- 未真实私信。
- 未真实评论。
- 未真实发帖。
- 未登录真实社媒账号。
- 生成内容均保持 `draft_only`。
- UI 输出中明确提示所有内容仅为草稿，不建议直接发布。

## 10. 已知限制

1. OpenClaw agent CLI 在自动汇总模式下仍可能卡住，Phase 2B 暂时默认关闭自动模型汇总验证。
2. 桌面 UI 路径已经跑通一次真实任务，但耗时较长，约 8 分钟完成完整 MD + DOCX 交付。
3. 当前 UI 中仍显示 LobsterAI 上游品牌，白标化未在本阶段处理。
4. 本阶段未接入真实社媒账号，也没有自动发布/评论/私信能力。
5. 公开搜索来源质量需要继续做去重、广告页过滤和来源可信度评分。

## 11. 结论

结论：B，能力部分成立，建议继续。

成立部分：

- 东莞制造业获客工作流已具备产品化 MVP 结构。
- domestic_signal_growth 能稳定生成制造业获客交付物。
- LobsterAI 桌面 UI 可以通过真实鼠标操作发起任务。
- DeepSeek V4 Pro UI 路径可进入真实执行。
- web-search、web_fetch、docx 在 UI 路径中被触发。
- 最终能生成可交付的 Markdown 推广方案和 Word 销售交接单。

待修部分：

- Dev Auto-Run 的 OpenClaw agent CLI 模型汇总需要单独修复，不应阻塞 Skill 产品化。
- UI 耗时较长，需要后续做任务进度提示、可中断、结果自动归档和更明确的交付入口。

## 12. 下一阶段建议

1. 进入 Phase 2C：把 UI 生成的 Markdown/DOCX 自动归档到宇智能项目工作区，并在控制台中可视化查看。
2. 修复 OpenClaw agent CLI 自动汇总卡住问题，或改为通过稳定 Gateway API 调用 DeepSeek V4 Pro。
3. 给公开来源增加可信度评分、广告页过滤、重复来源合并。
4. 做“制造业老板输入表单”：产品、客户类型、产能、交期、认证、可公开素材、禁止承诺项。
5. 继续保持外部动作 `draft_only`，发布、评论、私信、邮件仍必须人工审批。

## 13. 回滚方式

- 回退本阶段 Git commit。
- 删除 `D:\OpenClaw\v2\workflows\dongguan_manufacturing_growth\`。
- 删除 `D:\OpenClaw\v2\test-cases\manufacturing_growth\`。
- 删除 `D:\OpenClaw\v2\config\yuzhineng-product-mode.example.json`。
- 如需清理 UI 运行结果，可删除：
  `C:\Users\Admin\AppData\Roaming\LobsterAI\openclaw\state\workspace-yuzhineng-content-agent\东莞电子连接件工厂推广方案.md`
  和
  `C:\Users\Admin\AppData\Roaming\LobsterAI\openclaw\state\workspace-yuzhineng-content-agent\工厂销售客户交接单.docx`
