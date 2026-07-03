# Phase 2F-Fix：独立 Agent 单聊与总控子节点清理报告

测试日期：2026-07-03

## 1. 用户反馈

用户指出两个问题：

1. 多 Agent 工作流把专业 Agent 又挂成了“制造业总控”下面的小一层子节点，层级容易混乱。
2. 上次修复后，只能在总控群聊里发任务，不能直接点各个 Agent 单独对话。

## 2. 根因

1. 上轮为了让总控会话能看到专业 Agent 产出，把专业 Agent 同时写入了 `subagent_runs/subagent_messages`。这会在总控任务下面出现一串不可继续对话的子 Agent 节点。
2. 上轮为了避免点击 Agent 行误开空任务，把 Agent 行点击改成只展开和刷新。结果普通用户点击某个 Agent 时，不再切换到该 Agent 的单聊输入区。

## 3. 修复策略

本轮明确区分两种对象：

- 专业 Agent：是左侧“我的 Agent”里的一等 Agent，可以单独对话、独立保存会话。
- 总控群聊摘要：只在总控会话正文里展示协作过程，不再在总控下面创建不可对话的子 Agent 节点。

## 4. 修改文件

主仓库已跟踪文件：

- `D:\OpenClaw\v2\scripts\real_agent_collaboration.py`
- `D:\OpenClaw\v2\tests\test_real_agent_collaboration.py`
- `D:\OpenClaw\v2\reports\PHASE_2F_FIX_AGENT_CHAT_AND_SUBAGENT_NODES_CN.md`

已实际修改但位于被主仓库忽略的 LobsterAI 上游源码目录：

- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\components\agentSidebar\AgentTreeNode.tsx`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\components\agentSidebar\AgentTreeNode.test.ts`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\components\agentSidebar\MyAgentSidebarTree.tsx`

说明：LobsterAI 上游源码目录当前被 `.gitignore` 排除。本机修复已生效，后续正式迁移时需要把这些改动固化进正式 fork 或可重复 patch。

## 5. 数据清理

清理前已备份 LobsterAI SQLite：

- `D:\OpenClaw\backups\lobsterai-sqlite\lobsterai-before-phase2f-remove-nested-subagents-20260703-133114.sqlite`

清理范围：

- 仅删除 `parent_session_id LIKE 'phase2f-%'` 的历史 `subagent_runs`。
- 同步删除这些 run 对应的 `subagent_messages`。
- 不删除任何真实 Agent。
- 不删除各专业 Agent 的独立 `cowork_sessions`。
- 不读取 secrets，不真实外发。

清理结果：

- 删除历史 Phase 2F 子 Agent run：37 条。
- 删除历史 Phase 2F 子 Agent 消息：36 条。
- 剩余 Phase 2F 总控子 Agent run：0 条。

## 6. 新任务验证

新跑了一次制造业多 Agent 工作流：

- 输入任务：推广东莞精密五金加工服务，目标客户是智能硬件品牌和跨境卖家。
- 结果文件：`D:\OpenClaw\v2\data\ui-runs\phase2f-fix-agent-chat\workflow-result.json`

SQLite 验证结果：

- Phase 2F 桌面会话数：9。
- 专业 Agent 独立会话数：8。
- 总控下面 `subagent_runs`：0。
- 示例独立 Agent 会话：
  - `yuzhineng-product-analyst`
  - `yuzhineng-opportunity-researcher`
  - `yuzhineng-content-producer`
  - `yuzhineng-factory-handoff`
  - `yuzhineng-archive-agent`

## 7. 鼠标级桌面验证

验证方式：Windows 本机窗口、鼠标点击和截图。当前没有可用的 Computer Use 插件，未使用浏览器作为主验证入口。

截图：

- LobsterAI 前台启动：`D:\OpenClaw\v2\data\ui-runs\phase2f-fix-agent-chat\lobsterai-focused.png`
- 点击“产品理解 Agent”后的单聊入口：`D:\OpenClaw\v2\data\ui-runs\phase2f-fix-agent-chat\lobsterai-product-agent-clicked.png`

验证结果：

- 点击左侧“产品理解 Agent”后，底部 Agent 选择器显示“产品理解 Agent”。
- 中央输入框保持可输入状态，可以对该 Agent 单独发任务。
- 总控会话下不再生成产品/商机/宣传等子 Agent 节点。
- 总控左侧仍保留总控自己的任务历史，这是正常任务记录，不是子 Agent。

## 8. 自动化测试

已执行：

```powershell
npx vitest run src/renderer/components/agentSidebar/AgentTreeNode.test.ts src/renderer/components/agentSidebar/useAgentSidebarState.test.ts src/renderer/components/agentSidebar/useSubagentSessions.test.ts
npm run compile:electron
python -m unittest D:\OpenClaw\v2\tests\test_real_agent_collaboration.py -v
python -m unittest discover D:\OpenClaw\v2\tests -v
python -m py_compile D:\OpenClaw\v2\scripts\real_agent_collaboration.py D:\OpenClaw\v2\scripts\run_manufacturing_multi_agent_workflow.py
```

结果：

- 前端测试：3 个文件、14 项通过。
- Electron 编译：通过。
- Phase 2F 相关 Python 测试：通过。
- v2 Python 测试发现：6 项通过。

## 9. 已知限制

1. 左侧仍会显示总控 Agent 自己的任务历史；这是可继续打开的总控会话，不是专业子 Agent。
2. 专业 Agent 仍以一等 Agent 显示在“我的 Agent”下，符合“可单独对话”的目标。
3. LobsterAI 源码目录仍被主仓库忽略，后续必须进入正式 fork 或 patch 管理。
4. 当前仍显示 LobsterAI 上游品牌，白标化不是本轮范围。

## 10. 结论

结论：修复通过。

现在的正确使用方式：

1. 要总控协作，就点“宇智能制造业获客总控 Agent”并发任务。
2. 要单独问某个专业 Agent，就直接点左侧对应 Agent，例如“产品理解 Agent”“商机发掘 Agent”“宣传物料 Agent”，底部切到该 Agent 后即可单聊。
3. 总控里只看协作摘要；专业 Agent 的独立产出和后续追问，走各自 Agent 的会话。
