# OpenClaw v2 Codex 规则

## 最高原则

本项目的最高开发原则是“开源优先、最小改动、可商用交付”。

任何新功能、新模块、新 PoC、新集成都必须按以下顺序判断：

1. 是否已有成熟开源项目可直接部署？
2. 是否已有官方 SDK 或官方 API 可直接接入？
3. 是否可以通过配置、插件、Webhook、CLI、MCP、Skill 调用？
4. 是否可以通过桥接脚本完成？
5. 是否只需要最小局部补丁？
6. 只有以上全部不满足，才允许自研最小版本。

## 禁止行为

- 禁止“参考开源项目后从零重写”。
- 禁止为了控制感而重写已有成熟组件。
- 禁止为了安全理由默认重写全部系统。
- 禁止为了 UI 好看而大规模重构底层。
- 禁止在没有用户价值验证前开发复杂后台。
- 禁止把旧控制台继续扩张成正式产品主线。
- 禁止读取 `secrets` 中的真实密钥。
- 禁止提交 API Key、Token、Cookie、浏览器 Profile。
- 禁止真实发送邮件、私信、评论、发帖。
- 禁止绕过验证码、登录墙或平台限制。
- 禁止提交旧 console、logs、database、backups、secrets、node_modules、dist、build、cache。

## 必须行为

- 每次实质开发前必须完成开源复用判断。
- 每次实质开发前必须写清楚最小改动范围。
- 每次实质开发后必须运行测试。
- 每次实质开发后必须输出中文报告。
- 每次涉及外部动作时必须通过 `safety_reviewer`。
- 每次涉及普通用户界面时必须通过 `product_fit_reviewer` 或 `ux_reviewer`。
- 每次涉及依赖安装、打包、部署时必须记录环境和失败原因。

## 工作流入口

所有后续实质开发任务必须先读取：

- `D:\OpenClaw\AGENTS.md`
- `D:\OpenClaw\v2\CODEX_WORKFLOW_CN.md`
- `D:\OpenClaw\v2\PHASE_GATE_CHECKLIST_CN.md`
- `D:\OpenClaw\v2\V2_FINAL_GOAL_CN.md`

旧 Phase 1.x 控制台只作为历史、调试和参考，不再作为正式产品主线扩张。

