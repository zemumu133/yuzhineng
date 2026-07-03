# Phase R0 项目路线重置报告

## 测试日期

2026-06-30

## 测试环境

- 系统：Windows
- 根目录：`D:\OpenClaw`
- v2 工作区：`D:\OpenClaw\v2`
- 控制台地址：`http://127.0.0.1:18880/`

## 目标

完成项目路线重置与 v2 工作区初始化。旧版 Phase 1.x 控制台保留为历史、调试和参考版本，v2 改为“成熟开源底座 + 国内获客 Skill/API/Workflow + 安全审批层”的产品路线。

本阶段不安装 LobsterAI、Sim.ai、PocketBase、SearXNG、Crawl4AI、Firecrawl 或 Meilisearch，不修改旧控制台业务逻辑，不删除旧文件。

## 操作步骤

1. 盘点 `D:\OpenClaw` 当前目录结构。
2. 检查 Git、Node.js、npm、pnpm、Python、Docker 可用性。
3. 检查 secrets、logs、database、backups、console、scripts、docs 等目录是否存在。
4. 检查旧控制台是否可访问。
5. 创建 `D:\OpenClaw\v2` 隔离工作区。
6. 创建 v2 产品方向、架构、阶段计划和组件决策日志。
7. 创建 PoC 报告模板。
8. 创建 v2 环境预检脚本。
9. 使用旧项目现有脚本启动控制台。
10. 执行备份并手工复核备份 zip。

## 成功项

- `D:\OpenClaw` 旧项目目录存在，核心目录未删除。
- `D:\OpenClaw\v2` 已创建。
- v2 路线文档已创建。
- v2 报告模板已创建。
- v2 预检脚本已创建：`D:\OpenClaw\v2\scripts\v2-preflight-check.ps1`。
- 旧控制台已通过现有脚本启动成功。
- 控制台访问测试通过：`http://127.0.0.1:18880/` 返回 HTTP 200。
- 备份 zip 已生成并可读取：`D:\OpenClaw\backups\openclaw-backup-20260630-121840.zip`。
- 备份 SHA256：`8F45F1CEF08E6549DAEF3541BA0A8B3F8562692401173BE5A08A2C9850BAAE2C`。
- v2 工作区未发现 secrets、logs、backups、node_modules、dist、build、cache 等高风险文件。

## 失败项

- Git 当前不可用，无法执行 Git 状态检查、创建 tag、创建 branch 或提交。
- `D:\OpenClaw` 当前未检测到 `.git` 目录。
- Docker 当前不可用，符合本阶段“不安装、不配置 Docker”的限制。
- 旧项目根目录未发现 `README.md`、`BACKLOG.md`、`AGENTS.md`、`SAFETY_RULES.md`、`TEST_PLAN.md`，因此未更新根 README/BACKLOG。
- 旧备份脚本生成了可读取 zip，但未正常退出并自动生成 manifest。

## 失败原因

- Git：当前 PowerShell PATH 中没有 `git`，常见安装路径也未发现 Git 可执行文件；同时 `D:\OpenClaw\.git` 不存在。
- Docker：未安装或未加入 PATH；本阶段明确跳过 Docker。
- 备份脚本：zip 已生成且可读取，但脚本卡在收尾阶段。已停止卡住的备份进程，并补充手工复核 manifest。

## 安全检查

- 未读取 `D:\OpenClaw\secrets` 中任何密钥内容。
- 未安装任何新软件。
- 未克隆任何 GitHub 仓库。
- 未运行远程安装脚本。
- 未删除旧项目文件。
- 未修改旧控制台业务逻辑。
- 未执行真实邮件、私信、评论、发帖或平台操作。
- v2 工作区未放入密钥、日志、缓存、构建产物或备份文件。

## 易用性判断

v2 工作区已经把产品方向、架构、阶段计划和组件决策拆成独立中文文档，方便后续按阶段推进。旧控制台仍可通过原地址打开，便于查看历史成果和调试。

## 商用可行性判断

R0 只完成路线重置和工作区初始化，尚未验证 LobsterAI、Sim.ai、搜索栈或会员系统。当前路线比继续从零堆旧控制台更适合商业化，因为后续会优先复用成熟开源底座，并把差异化能力集中在国内获客 Skill/API/Workflow。

## 是否建议继续

建议继续，但进入 Phase 1A 前应先处理 Git 缺失问题。Git 可用后应补做：

1. 初始化或迁移 Git 仓库。
2. 创建 `legacy-console-phase-1-9A` tag。
3. 创建 `v2-open-source-growth-system` branch。
4. 提交 R0 文档和脚本。

## 下一步建议

进入 Phase 1A：LobsterAI PoC。

建议先只做源码和文档审查，不安装、不运行未知脚本。确认来源、许可证、更新活跃度、安装方式、打包方式和安全风险后，再决定是否正式试装。

