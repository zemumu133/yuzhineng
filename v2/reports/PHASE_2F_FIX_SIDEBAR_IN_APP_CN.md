# Phase 2F-FixSidebar：LobsterAI 左侧 Agent 任务预览与桌面内集成修复报告

测试日期：2026-07-03

## 1. 本轮目标

修复用户在 LobsterAI 桌面端看到的两个核心问题：

1. 左侧 Agent 任务预览刷新不稳定，外部写入的多 Agent 任务不容易显示。
2. 多 Agent 成果被误导到本地网页调试页，用户希望全部整合进 LobsterAI，不额外创建网页会话。

本轮不做白标化、不接真实社媒账号、不真实发邮件/私信/评论/发帖、不读取 secrets。

## 2. 根因

1. LobsterAI 左侧 `useAgentSidebarState` 只在初次加载和 Redux 会话变化时合并数据。Phase 2F 的工作流会直接写入 LobsterAI 本地 SQLite，但运行中的桌面端没有稳定收到刷新事件，因此左侧任务预览容易停留在旧状态。
2. 左侧 Agent 行点击逻辑同时触发展开和新建任务，用户点击 Agent 时可能被带到空会话，感觉“随便找个 Agent 不能正常工作”。
3. Phase 2F 写入 `subagent_runs.status = completed`，而 LobsterAI 子 Agent 详情更符合 `running / done / error` 状态体系，导致子 Agent 展示不稳定。
4. Phase 2F 报告仍把 HTML 工作台作为显眼入口，容易让用户误解为产品变成网页端。
5. Electron 直接启动时存在两个本地运行问题：`package.json main` 指向旧构建路径，且当前 CommonJS preload 在 sandbox 下无法注入 `window.electron`。

## 3. 修改文件清单

主仓库已跟踪文件：

- `D:\OpenClaw\v2\scripts\real_agent_collaboration.py`
- `D:\OpenClaw\v2\scripts\run_manufacturing_multi_agent_workflow.py`
- `D:\OpenClaw\v2\tests\test_real_agent_collaboration.py`
- `D:\OpenClaw\v2\reports\PHASE_2F_FIX_SIDEBAR_IN_APP_CN.md`

已实际修改但位于被主仓库忽略的 LobsterAI 上游源码目录：

- `D:\OpenClaw\v2\client-shell\lobsterai\src\package.json`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\main\main.ts`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\components\agentSidebar\constants.ts`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\components\agentSidebar\useAgentSidebarState.ts`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\components\agentSidebar\MyAgentSidebarTree.tsx`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\components\agentSidebar\AgentTreeNode.tsx`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\components\agentSidebar\useAgentSidebarState.test.ts`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\components\agentSidebar\AgentTreeNode.test.ts`

说明：`D:\OpenClaw\v2\client-shell\lobsterai\src\` 当前被 `.gitignore` 排除，避免提交整份上游源码、依赖和构建产物。本报告记录本地修复点，后续如进入正式 fork，应将这些补丁固化到 fork 或可重复 patch。

## 4. 桌面端左侧刷新修复

本轮在 LobsterAI 左侧 Agent 树中增加了更接近用户实际使用的刷新机制：

- 新增 Agent 任务预览刷新入口 `refreshAgentTaskPreviews`。
- 监听 `cowork:sessions:changed` 后刷新所有启用 Agent 的预览。
- 窗口获得焦点、页面恢复可见时刷新预览。
- 页面可见时每 8 秒轻量刷新一次，解决外部工作流直接写入 SQLite 后桌面端不更新的问题。
- 点击 Agent 行只负责展开和刷新，不再自动创建空任务。
- 新建任务仍保留在右侧 compose 图标上。

## 5. 多 Agent 成果整合到 LobsterAI

`real_agent_collaboration.py` 已调整 LobsterAI 镜像写入：

- 子 Agent run 状态从 `completed` 改为 `done`。
- 每个子 Agent run 同时写入用户任务输入和助手产出，方便在 LobsterAI 子 Agent 详情里查看“它拿到了什么任务、输出了什么结果”。
- 总控 Agent 会话输出加入可读摘要：参与 Agent、工作群摘要、归纳 Agent 总结、返工数量、draft_only 安全声明。

`run_manufacturing_multi_agent_workflow.py` 已调整报告文案：

- 普通用户主入口改为 LobsterAI 桌面端左侧“我的 Agent”。
- 总控 Agent 会话用于查看子 Agent 协作记录。
- HTML 工作群和工作台仅作为开发验收归档，不再作为普通用户主入口。

## 6. Electron 启动修复

为了能直接启动 LobsterAI 桌面端并完成真实鼠标验证，本轮修复：

- `package.json` 的 `main` 从旧路径改为 `dist-electron/main/main.js`。
- `main.ts` 增加 preload 路径候选解析，兼容当前编译输出。
- 当前 CommonJS preload 需要读取本地模块，因此主渲染窗口临时使用 `sandbox: false`。同时保留 `nodeIntegration: false` 和 `contextIsolation: true`。

风险说明：这是开发验证阶段的本地兼容修复。后续正式发布前建议把 preload 构建成独立安全包，再评估是否恢复主窗口 sandbox。

## 7. 数据库修复

已备份并修复历史 Phase 2F 子 Agent 状态：

- 备份文件：`D:\OpenClaw\backups\lobsterai-sqlite\lobsterai-before-phase2f-sidebar-status-repair-20260703-122750.sqlite`
- 修复范围：仅更新 `subagent_runs.status = completed` 且 `parent_session_id LIKE 'phase2f-%'` 的历史记录。
- 更新结果：18 条历史记录改为 `done`。
- 未读取 secrets，未改浏览器 Profile，未真实外发。

## 8. 鼠标级桌面验证

本轮没有把浏览器或静态 HTML 当作主验证路径。验证方式为 Windows 本机鼠标/窗口自动化，直接操作 LobsterAI 桌面窗口。

验证截图：

- `D:\OpenClaw\v2\data\ui-runs\phase2f-fix-sidebar\lobsterai-preload-fixed.png`
- `D:\OpenClaw\v2\data\ui-runs\phase2f-fix-sidebar\lobsterai-chief-task-opened.png`
- `D:\OpenClaw\v2\data\ui-runs\phase2f-fix-sidebar\lobsterai-product-subagent-opened.png`
- `D:\OpenClaw\v2\data\ui-runs\phase2f-fix-sidebar\lobsterai-opportunity-subagent-opened.png`
- `D:\OpenClaw\v2\data\ui-runs\phase2f-fix-sidebar\lobsterai-third-subagent-opened.png`

验证结果：

- LobsterAI 桌面端可启动。
- 左侧“我的 Agent”下显示宇智能总控 Agent 和专业 Agent 任务预览。
- 点击总控任务可在 LobsterAI 内打开任务详情。
- 总控会话下方显示子 Agent 协作记录。
- 点击产品理解、商机发掘、宣传物料等子 Agent，可打开对应子 Agent 详情。
- 子 Agent 详情显示任务输入、执行输出、产出路径和 draft_only 安全声明。
- 未打开新的网页会话作为用户主入口。

## 9. 测试结果

已执行测试：

```powershell
npx vitest run src/renderer/components/agentSidebar/useAgentSidebarState.test.ts src/renderer/components/agentSidebar/AgentTreeNode.test.ts src/renderer/components/agentSidebar/useSubagentSessions.test.ts
npm run compile:electron
python -m unittest D:\OpenClaw\v2\tests\test_real_agent_collaboration.py -v
python -m unittest discover D:\OpenClaw\v2\tests -v
python -m py_compile D:\OpenClaw\v2\scripts\run_manufacturing_multi_agent_workflow.py D:\OpenClaw\v2\scripts\real_agent_collaboration.py
```

结果：

- Agent Sidebar 与子 Agent 会话前端逻辑测试：3 个测试文件、14 个测试通过。
- Electron 编译：通过。
- Phase 2F 多 Agent 工作流测试：通过。
- v2 Python 测试发现：6 项通过。
- 鼠标级 LobsterAI 桌面验证：通过。

备注：`npm test` 会先执行 `npm rebuild better-sqlite3`。当前本机 Node 24 与 Electron 40 会在 `better_sqlite3.node` 的 Node ABI / Electron ABI 之间切换；在缺少完整 Windows SDK 时，`npm test` 的 pretest 会被原生模块重建卡住。本轮前端逻辑验证使用 `npx vitest run ...` 绕开原生 SQLite 重建；桌面端原生模块可用性由 `npm run compile:electron` 和实际 LobsterAI 鼠标验证覆盖。

## 10. 已知限制

1. LobsterAI 上游源码目录仍被主仓库忽略，本轮源码补丁在本机生效，但正式迁移前需要进入 fork 或生成可重复 patch。
2. 当前左侧刷新采用事件 + 焦点刷新 + 8 秒轮询，足够解决本机外部写入可见性问题；长期建议改成所有工作流都通过 LobsterAI IPC 或内部服务写入，减少轮询。
3. HTML 工作群和工作台文件仍会作为开发验收归档生成，但不再作为普通用户主入口。后续可以加 debug 开关默认关闭。
4. 主窗口 `sandbox: false` 是为了兼容当前 CommonJS preload。正式发布前需要做 preload 安全重构。
5. 当前仍显示 LobsterAI 上游品牌，白标化不在本轮范围。

## 11. 回滚方式

1. 回退主仓库本阶段 Git commit。
2. 如需回滚 LobsterAI 本地源码修改，可重新解压/恢复 LobsterAI 上游源码目录，或按本报告第 3 节逐项撤销。
3. 如需回滚历史 SQLite 状态修复，可用备份文件：
   `D:\OpenClaw\backups\lobsterai-sqlite\lobsterai-before-phase2f-sidebar-status-repair-20260703-122750.sqlite`

## 12. 结论

结论：B+，LobsterAI 桌面内多 Agent 协作查看路径已经可用。

用户现在应优先从 LobsterAI 左侧“我的 Agent”进入宇智能总控任务和各专业 Agent 任务，不再把本地 HTML 当作主要产品入口。下一阶段建议做两件事：

1. 把“多 Agent 项目群 / 工作群摘要”做成 LobsterAI 内一等入口，而不是只挂在总控会话和子 Agent 详情下。
2. 将本轮 LobsterAI 源码补丁固化到正式 fork 或可重复 patch 脚本，提升可迁移性。
