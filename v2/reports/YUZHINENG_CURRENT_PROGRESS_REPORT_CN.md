# 宇智能项目当前完整进度报告

生成日期：2026-07-03  
当前分支：`v2-open-source-growth-system`  
当前提交：`5e4b4214d872dba8de83c2647f21932f2dcec456`  
项目定位：面向中小企业，优先聚焦东莞制造业的 AI 获客与内容运营客户端。  

## 1. 当前总状态

宇智能已经从早期 OpenClaw 本地控制台路线，转向 v2 的“LobsterAI 桌面客户端 + OpenClaw runtime + DeepSeek V4 Pro + 本地 Skill / 工作流”的路线。

当前不是纯概念阶段，也不是只会聊天的 Demo。现在已经具备一个可演示、可测试、可重复运行的制造业获客 MVP：

1. 用户可以在 LobsterAI 桌面端选择宇智能相关 Agent。
2. 用户可以输入制造业推广任务。
3. 系统可以生成产品理解、商机判断、内容草稿、社媒计划、评论/私信草稿、工厂销售交接单和项目报告。
4. 多 Agent 工作流可以把任务拆给总控、产品理解、商机、内容、社媒、工厂交接、风控、归纳、归档等角色。
5. 所有外部动作保持 `draft_only`，不真实发布、不评论、不私信、不发邮件。
6. 结果可以归档到本地项目工作区。
7. 最新修复后，各专业 Agent 是左侧一等 Agent，可以单独对话；总控里不再挂不可继续对话的子 Agent 节点。

总体判断：当前处于“能力闭环 MVP 已成立，但产品化体验和正式可交付版本尚未完成”的阶段。

## 2. 已完成阶段

| 阶段 | 状态 | 主要成果 |
|---|---|---|
| R0 / R0.5 | 完成 | v2 路线重置、治理规则、阶段门禁、Git 基线 |
| 1A-Fast | 完成 | LobsterAI 安装、启动、Electron UI PoC |
| 1A-RepairRuntime | 完成 | Git Bash / OpenClaw runtime 修复，Cowork 可启动 |
| 1A-CommercialSurfaceAudit | 完成 | LobsterAI 商业化暴露面审计，白标化延后 |
| 1A-CapabilityFirst | 完成 | 验证 LobsterAI + OpenClaw + Skill 作为底座可继续 |
| 1A-E2E / UI-E2E | 部分成立 | DeepSeek V4 Pro 路由、Skill 同步、UI 任务发起路径验证 |
| 2A | 完成 | `domestic_signal_growth` 从占位升级为真实获客 Skill MVP |
| 2B | 完成 | 东莞制造业获客工作流 MVP |
| 2C | 完成 | 项目归档、项目工作区、结果查看入口 |
| 2D | 完成 | 产品资料理解 Skill 和产品资料卡增强 |
| 2E | 完成 | 多 Agent 总控协作工作流 MVP |
| 2F | 完成并修复 | 真实多 Agent 协作、群聊摘要、归纳 Agent、左侧 Agent 展示和单聊修复 |

## 3. 当前项目目录能力

当前 v2 主要目录：

- `D:\OpenClaw\v2\client-shell\lobsterai`：LobsterAI 桌面客户端底座。
- `D:\OpenClaw\v2\skills\domestic_signal_growth`：国内获客信号与内容建议 Skill。
- `D:\OpenClaw\v2\skills\product_intelligence`：产品资料理解 Skill。
- `D:\OpenClaw\v2\skills\manufacturing_multi_agent_workflow`：制造业多 Agent 工作流 Skill。
- `D:\OpenClaw\v2\workflows\dongguan_manufacturing_growth`：东莞制造业获客工作流定义。
- `D:\OpenClaw\v2\scripts`：归档、自动测试、工作流执行、启动脚本。
- `D:\OpenClaw\v2\projects`：本地项目成果归档目录，已被 Git 忽略。
- `D:\OpenClaw\v2\data`：运行数据、UI 测试轨迹，已被 Git 忽略。
- `D:\OpenClaw\v2\reports`：阶段报告和当前进度报告。

当前已存在的核心 Skill：

1. `domestic_signal_growth`
2. `product_intelligence`
3. `manufacturing_multi_agent_workflow`

当前已存在的核心脚本：

1. `start-yuzhineng.ps1`
2. `dev-autorun-gate.py / .ps1`
3. `run_manufacturing_multi_agent_workflow.py / .ps1`
4. `real_agent_collaboration.py`
5. `archive_manufacturing_growth_result.py / .ps1`
6. `v2-task-precheck.ps1`
7. `v2-task-postcheck.ps1`

## 4. 现在能做什么

### 4.1 桌面端使用

当前 LobsterAI 桌面端可以作为宇智能的主要交互入口。用户可以：

- 打开 LobsterAI。
- 选择 DeepSeek V4 Pro。
- 在左侧选择总控 Agent 或专业 Agent。
- 对总控 Agent 发起多 Agent 工作流任务。
- 对产品理解、商机发掘、内容、社媒、工厂交接等专业 Agent 单独对话。
- 查看任务历史和生成结果。

最近修复结果：

- 左侧 Agent 任务预览会刷新。
- 专业 Agent 不再被挂成总控下面的小节点。
- 专业 Agent 可以单独对话。
- 总控会话只保留协作摘要，不再塞不可继续对话的子 Agent 详情。

### 4.2 DeepSeek V4 Pro 调用

当前 DeepSeek V4 Pro 路由已经成立：

- OpenClaw Gateway 日志曾验证 agent model 为 `deepseek/deepseek-v4-pro`。
- LobsterAI UI 中模型选择可显示 DeepSeek V4 Pro。
- 多个 UI 任务和 Skill 任务已经通过 DeepSeek V4 Pro 路径完成。

当前不把 Codex 当作普通 Agent fallback。Codex OAuth 曾不可用，因此高级审核主要由 DeepSeek 双审或本地风控逻辑替代。

### 4.3 公开信息研究与获客判断

`domestic_signal_growth` 已经可以：

- 接收产品、行业、城市、目标客户、平台、模式等输入。
- 调用公开搜索适配层。
- 输出公开来源。
- 判断商机。
- 生成目标客户类型。
- 生成平台策略。
- 生成评论草稿、私信草稿、待办、风险提示和下一步建议。

已验证行业：

- 职业证书考评服务。
- 重型包装纸箱服务。
- 健身器材。
- 电子配件 / 电子连接件。

### 4.4 产品资料理解

`product_intelligence` 已经可以：

- 读取制造业产品资料。
- 输出产品画像。
- 提炼卖点。
- 判断适合客户。
- 整理应用场景。
- 生成内容角度。
- 生成销售跟进重点。
- 标记缺失资料。
- 生成产品资料卡 `product_card.md`。

已验证样例：

- 东莞重型包装纸箱厂。
- 东莞健身器材厂。
- 东莞电子配件厂。

### 4.5 制造业获客工作流

`dongguan_manufacturing_growth` 工作流已经可以生成：

- 产品理解。
- 商机发掘。
- 小红书内容方向。
- 抖音脚本方向。
- 公众号大纲。
- 销售话术。
- 评论回复草稿。
- 私信草稿。
- 账号养成计划。
- 工厂销售交接单。
- 人工待办。
- 风险提示。
- 下一步建议。

所有这些结果默认是 `draft_only`，不能自动真实发布或发送。

### 4.6 多 Agent 协作

当前已经具备受控多 Agent 协作 MVP。角色包括：

- 宇智能制造业获客总控 Agent。
- 产品理解 Agent。
- 商机发掘 Agent。
- 宣传物料 Agent。
- 社媒运营 Agent。
- 工厂对接 Agent。
- 风控审核 Agent。
- 归纳 Agent。
- 归档 Agent。

当前多 Agent 的实现方式是：

1. 总控 Agent 接收任务。
2. 受控本地执行器拆解任务。
3. 每个专业 Agent 生成独立任务和输出。
4. 风控 Agent 进行返工检查。
5. 归纳 Agent 汇总最终结果。
6. 归档 Agent 保存项目成果。
7. LobsterAI 左侧显示各专业 Agent 的独立会话。

重要边界：

- 目前不是 OpenClaw 原生“Agent 互相自由调用”的复杂系统。
- 当前是“总控 Agent + 受控执行器 + 专业 Agent 视角产出”的安全 MVP。
- 这样做更可控，不会让模型自由执行系统命令或外部动作。

### 4.7 项目成果归档

当前可以把生成结果归档为项目工作区。项目目录通常包含：

- `input.json`
- `project_manifest.json`
- `sources.json`
- `skill_output.json`
- `report.md`
- `handoff.docx`
- `todos.json`
- `safety_check.json`
- `README_CN.md`
- `product_card.md`
- `multi_agent/agent_tasks.json`
- `multi_agent/group_room_messages.json`
- `multi_agent/files/final_summary.md`

已生成本地项目索引：

- `D:\OpenClaw\v2\projects\projects_index.json`
- `D:\OpenClaw\v2\projects\index.html`

注意：当前项目索引主要还是本地 HTML / 文件入口，尚未完全整合成 LobsterAI 内置“成果中心”。

## 5. 当前不能做什么

当前明确不能或不应做：

1. 不能自动真实发帖。
2. 不能自动真实评论。
3. 不能自动真实私信。
4. 不能自动真实发邮件。
5. 不能绕过验证码、登录墙、平台风控。
6. 不能抓取非公开数据。
7. 不能编造联系方式。
8. 不能把草稿当成真实执行结果。
9. 不能把静态 HTML 调试页当成正式产品体验。
10. 不能把 LobsterAI 上游源码目录的本地改动视为已经正式固化。
11. 不能对外宣称已经是完整商业可交付 SaaS。
12. 不能对外承诺自动获客、自动成交或收益结果。

## 6. 当前主要风险

### 6.1 LobsterAI 上游源码改动未正式固化

最近几轮为了修复左侧 Agent 展示、单聊和 Electron 启动，改动了 LobsterAI 上游源码目录：

`D:\OpenClaw\v2\client-shell\lobsterai\src`

但该目录当前被 `.gitignore` 排除，避免提交整份上游源码、依赖和构建产物。这是合理的，但也带来一个风险：

- 本机已经修好。
- Git 主仓库没有直接跟踪这些源码文件。
- 后续迁移、重装、换电脑时，必须进入正式 fork 或生成可重复 patch，否则容易丢失修复。

优先级：高。

### 6.2 项目成果入口还不够产品化

现在成果可以生成、可以归档，但入口分散在：

- LobsterAI 会话。
- 本地项目目录。
- `projects/index.html`。
- 阶段报告。

普通用户仍可能不知道“成果在哪里、下一步点哪里”。

优先级：高。

### 6.3 Skill 在 LobsterAI UI 中的可见性还不够强

`product_intelligence`、`domestic_signal_growth`、`manufacturing_multi_agent_workflow` 已经存在，但在 UI 上还没有形成非常清晰的“点击这个按钮就能启动对应能力”的产品入口。

优先级：高。

### 6.4 搜索质量仍需增强

当前公开搜索适配层能跑，但还需要继续做：

- 去重。
- 广告页过滤。
- 来源可信度评分。
- 行业来源白名单。
- 搜索失败时的友好提示。
- URL 导入 / 手工来源补充。

优先级：中高。

### 6.5 仍显示 LobsterAI / 网易有道品牌和上游入口

商业化暴露面审计已完成，但白标化暂缓。当前桌面端仍可看到 LobsterAI、网易有道、官方登录、官方协议、官方服务等痕迹。

这不影响当前能力验证，但影响对外试用和商业交付。

优先级：中，能力闭环稳定后再做。

### 6.6 安全与权限还需要产品化表达

当前技术层面保持 `draft_only`，但普通用户界面里仍需要更清楚地区分：

- 草稿。
- 待审核。
- 已人工执行。
- 风险高。
- 不建议执行。

优先级：中高。

## 7. 下一步要做什么

### P0：固化 LobsterAI 补丁

目标：让本机修复可迁移、可重装、可提交、可回滚。

建议做法：

1. 建立正式 LobsterAI fork 或 vendor patch 目录。
2. 把左侧 Agent 刷新、单聊入口、preload/Electron 启动修复做成可重复 patch。
3. 给 patch 增加应用脚本和校验脚本。
4. 报告中明确上游 commit、patch 文件、应用方式和回滚方式。

这是当前最重要的工程债。

### P0：做 LobsterAI 内置成果中心

目标：用户不用打开本地 HTML，不用找文件夹。

建议做：

1. 左侧增加“项目 / 成果”入口或复用现有项目入口。
2. 显示项目列表。
3. 显示每个项目的报告、产品资料卡、内容草稿、交接单、待办。
4. 支持打开本地文件。
5. 支持标记“已人工执行 / 待修改 / 已驳回”。

### P1：明确多 Agent 工作台体验

目标：让用户能看懂“谁在做什么”。

建议做：

1. 总控 Agent 负责发起和总结。
2. 专业 Agent 负责单聊和独立追问。
3. 项目群显示协作摘要，不再混成不可对话子节点。
4. UI 上明确显示：
   - 当前任务。
   - 参与 Agent。
   - 每个 Agent 输出。
   - 风控返工。
   - 归纳总结。

### P1：公开搜索与来源质量升级

目标：减少垃圾来源，提高报告可信度。

建议做：

1. 搜索关键词扩展。
2. 来源去重。
3. 来源可信度评分。
4. 低质广告页过滤。
5. 来源引用统一显示。
6. 搜索不可用时允许用户导入 URL。

### P1：制造业老板输入表单

目标：降低用户提问门槛。

建议做一个轻量表单：

- 工厂类型。
- 产品名称。
- 材料 / 规格。
- 产能。
- 交期。
- 认证。
- 典型客户。
- 目标客户。
- 禁止承诺项。
- 可公开素材。

表单生成结构化输入，再交给总控 Agent。

### P2：审批和待办中心

目标：把评论、私信、发布、邮件等外部动作全部变成可审查待办。

建议做：

- 待发布内容。
- 待回复评论。
- 私信草稿。
- 邮件草稿。
- 人工联系建议。
- 标记已人工执行。
- 驳回 / 退回修改。
- 风险等级。

不做“批准并自动发送”。

### P2：白标化和商业化准备

目标：从能力验证进入对外试用。

建议做：

1. 产品名、Logo、协议、关于页改为宇智能。
2. 保留开源许可证与必要版权声明。
3. 隐藏或隔离 LobsterAI / 网易有道官方登录、Portal、官方模型服务、自动更新、遥测。
4. 设计自己的更新策略和配置策略。
5. 明确 DeepSeek / OpenAI-compatible provider 的配置入口。

### P3：会员授权和打包

目标：做可分发版本。

建议做：

1. 最小会员授权。
2. 本机激活码或轻量账号。
3. Windows 打包。
4. 安装路径、数据路径、备份路径规范。
5. 一键启动、日志、恢复脚本。

## 8. 建议下一阶段路线

推荐进入：

**Phase 2G：LobsterAI 补丁固化 + 宇智能成果中心 MVP**

本阶段目标：

1. 把本机 LobsterAI 源码改动变成可重复 patch。
2. 在 LobsterAI 内提供“成果中心 / 项目结果”入口。
3. 让用户打开一个项目后，能看到：
   - 总报告。
   - 产品资料卡。
   - 内容草稿。
   - 社媒计划。
   - 销售交接单。
   - 待办。
   - 风控说明。
4. 不做真实外发。
5. 不做白标化大改。

原因：

- 当前能力已经能跑。
- 最大痛点已经不是“能不能生成”，而是“用户在哪里看、怎么继续用、怎么迁移”。
- 先固化补丁和成果中心，比继续堆更多 Agent 更重要。

## 9. 当前验收状态

当前可认为已通过的验收：

- DeepSeek V4 Pro 路由可用。
- LobsterAI 桌面端可启动。
- OpenClaw Gateway 可启动。
- domestic_signal_growth Skill 可运行。
- product_intelligence Skill 可运行。
- 制造业获客工作流可运行。
- 多 Agent 工作流可生成独立 Agent 输出。
- 各专业 Agent 可在 LobsterAI 左侧单独对话。
- 项目结果可归档。
- 报告、交接单、待办、安全检查可生成。
- 所有外部动作保持 draft_only。

当前未通过或未完成的验收：

- LobsterAI 本地源码补丁尚未正式固化。
- 成果中心还不是 LobsterAI 内置正式入口。
- 搜索质量还不是商业级。
- Skill 按钮和行业模板入口不够显眼。
- 白标化未做。
- 会员授权未做。
- 正式 Windows 打包未做。
- 真实审批中心未完全产品化。

## 10. 给用户的当前使用建议

现在最稳的使用方式：

1. 打开 LobsterAI。
2. 如果要跑完整制造业获客任务，选择“宇智能制造业获客总控 Agent”。
3. 输入类似：
   “我要推广东莞五金冲压件工厂，目标客户是家电厂、智能硬件品牌和跨境卖家。请用多 Agent 协作完成产品理解、机会判断、内容建议、社媒动作、工厂交接、风控审核和归纳总结；不要真实发布、不要私信、不要评论、不要发邮件。”
4. 如果要追问某个部分，直接点左侧对应 Agent：
   - 产品理解 Agent
   - 商机发掘 Agent
   - 宣传物料 Agent
   - 社媒运营 Agent
   - 工厂对接 Agent
   - 风控审核 Agent
5. 所有生成内容先作为草稿看，不要直接发布。

## 11. 一句话结论

宇智能目前已经具备“制造业 AI 获客工作流 MVP”的核心能力：能理解产品、判断商机、生成内容、形成待办、输出交接单、进行多 Agent 协作和本地归档。下一步最该做的不是继续加更多功能，而是把 LobsterAI 补丁固化、把成果中心做进桌面端、把用户体验从“工程可用”推进到“老板能用”。
