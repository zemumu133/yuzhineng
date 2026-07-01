# Phase 1A-E2E：DeepSeek V4 Pro + domestic_signal_growth + Cowork 最小闭环报告

测试日期：2026-07-01  
项目名称：宇智能  
测试范围：LobsterAI Electron dev、OpenClaw runtime、DeepSeek V4 Pro 路由、`domestic_signal_growth` 本地 Skill、Cowork/Gateway 会话调用。  
安全边界：未读取 `D:\OpenClaw\secrets`，未提交 API Key/Token/Cookie，未登录社媒，未真实发送邮件/私信/评论/发帖。

## 1. 当前 LobsterAI commit

- 上游仓库：`https://github.com/netease-youdao/LobsterAI`
- 当前源码来源：Phase 1A-Fast 获取的上游源码快照，源码目录被 `.gitignore` 排除。
- 已记录上游 commit：`b2317e65785ec02e982895c98c4c82d36d37d5f0`
- 本阶段基线 commit：`d7c46b44e5f9746cc281bf7b92edce7037016ed0`

## 2. OpenClaw runtime 状态

结论：可用。

验证命令：

```powershell
npm run electron:dev:openclaw
```

结果摘要：

- OpenClaw runtime 命中已构建缓存。
- Electron dev UI 成功启动。
- OpenClaw gateway 成功启动并进入 ready。
- Gateway 端口：`18790`。
- Gateway health 通过。

注意：启动过程中可选插件 `moltbot-popo` 网络拉取出现 `ECONNRESET`，脚本按 optional plugin 降级跳过，不影响本阶段核心验证。

## 3. Cowork mode 状态

结论：基础可用，但本轮未完成 Cowork 对话框真实发起任务。

已确认：

- CoworkProxy 启动。
- IMGatewayManager 创建 Cowork handler。
- Gateway 能由 Cowork 流程拉起。
- `sessions.create` 写入会话的 CLI 代发路径被 OpenClaw 设备 scope upgrade 门禁拦截。

未完成：

- 未能由 Codex 自动替用户在 Electron Cowork UI 输入并发送业务任务。
- 未能通过 CLI 代替 Cowork 完成 `sessions.create` 业务任务调用。

阻塞原因：

- CLI 当前只有 `operator.read` 能力。
- 创建/发送会话需要 `operator.write`。
- Gateway 返回：scope upgrade pending approval。
- `devices approve` 又需要 `operator.pairing`，同样触发 scope upgrade。

该阻塞属于 OpenClaw 本地设备权限门禁，不是 DeepSeek、runtime 或 Skill 本身失败。

## 4. 自动更新是否已临时禁用

结论：已在开发环境临时禁用。

方式：

- 创建本地企业配置包：`%APPDATA%\LobsterAI\enterprise-config\manifest.json`
- 设置：

```json
{
  "disableUpdate": true,
  "sync": {
    "openclaw": false,
    "skills": "merge",
    "agents": false,
    "mcp": false,
    "plugins": false
  }
}
```

验证结果：

- 启动日志显示检测到“宇智能 Phase 1A E2E 本地能力包”。
- 启动日志显示同步 1 个 Skill。
- 本轮启动未再次触发官方安装包下载。
- 旧的 persisted ready update 记录因文件不存在被清理。

回滚方式：

```powershell
Remove-Item -LiteralPath "$env:APPDATA\LobsterAI\enterprise-config" -Recurse -Force
```

## 5. DeepSeek V4 Pro 是否可选

结论：可选。

已确认：

- DeepSeek provider 存在。
- 模型列表包含：
  - `deepseek-v4-flash`
  - `deepseek-v4-pro`
  - `deepseek-reasoner`
- OpenClaw runtime 配置中 provider 保持现有 API Key 引用方式，未写入真实 key。

## 6. DeepSeek V4 Pro 是否成功调用

结论：未能完成一次模型内容调用。

已完成：

- 已将 OpenClaw runtime 主模型切换到 `deepseek/deepseek-v4-pro`。
- Gateway 启动日志证明：
  - `deepseek/deepseek-v4-pro model configured, enabled automatically`
  - `agent model: deepseek/deepseek-v4-pro`

未完成：

- 由于 CLI 代发 Cowork 会话被 `operator.write` 权限升级门禁拦截，未能完成一次业务任务模型响应。

判断：

- V4 Pro 路由成立。
- V4 Pro 实际生成业务内容尚未由 Cowork/Gateway 完整证明。

## 7. 是否能证明当前任务使用 V4 Pro

结论：只能证明 Gateway 当前任务路由默认已切到 V4 Pro，不能证明本轮业务任务完成了 V4 Pro 内容生成。

证据：

- `C:\Users\Admin\AppData\Roaming\LobsterAI\openclaw\state\openclaw.json` 当前主模型为 `deepseek/deepseek-v4-pro`。
- Gateway 启动日志显示 agent model 为 `deepseek/deepseek-v4-pro`。

缺口：

- `sessions.create` 未越过本地写权限门禁，因此没有生成最终业务回复。

## 8. domestic_signal_growth 接入方式

结论：已完成最小 Skill 接入。

新增/修改：

- `D:\OpenClaw\v2\skills\domestic_signal_growth\SKILL.md`
- `D:\OpenClaw\v2\skills\domestic_signal_growth\hello_growth.ps1`

接入方式：

- 使用 LobsterAI 原生企业配置 `skills=merge`。
- 本地能力包路径：`%APPDATA%\LobsterAI\enterprise-config\skills\domestic_signal_growth`
- 同步后用户 Skill 路径：`%APPDATA%\LobsterAI\SKILLs\domestic_signal_growth`
- OpenClaw runtime `skills.load.extraDirs` 指向 `%APPDATA%\LobsterAI\SKILLs`。

直接运行验证：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\OpenClaw\v2\skills\domestic_signal_growth\hello_growth.ps1" -InputJson '{"product":"职业证书考评服务","target_customers":["培训机构","人力资源公司"],"platforms":["小红书","抖音"],"mode":"draft_only"}'
```

结果：成功输出 JSON，包含商机判断、目标客户类型、小红书内容建议、抖音内容建议、跟进草稿、待办、风险提醒。

## 9. domestic_signal_growth 是否被 Cowork 调用

结论：未完成 Cowork 调用证明。

已完成：

- Skill 已同步到 LobsterAI 用户 Skill 目录。
- Skill 已可被本地 PowerShell 直接调用。
- Runtime 配置已加载 Skill extraDirs。

未完成：

- Cowork 会话发起被本机 CLI 写权限门禁阻塞，未产生模型调用 Skill 的完整轨迹。

## 10. web-search 是否被调用

结论：本轮 E2E 业务任务未调用成功；web-search bridge 可用。

已确认：

- Web Search Bridge Server 成功启动。
- 端口：`8923`。
- 历史/本地日志中存在公开搜索调用记录。

未完成：

- 因 Cowork 会话写入被拦截，本轮业务任务没有完成新的 web-search 调用。

## 11. 最小业务任务输入

```text
我要推广职业证书考评服务，目标客户是培训机构和人力资源公司。请用 DeepSeek V4 Pro，必要时用 web-search 查公开信息，并调用 domestic_signal_growth。输出商机判断、目标客户类型、小红书内容建议、抖音内容建议、跟进话术草稿和待办。不要真实发布，不要私信，不要评论，不要发邮件。
```

## 12. 最小业务任务输出摘要

完整 Cowork/Gateway 输出：未生成。

本地 `domestic_signal_growth` 直接运行输出摘要：

- 商机判断：职业证书考评服务适合先用公开信息研究、痛点内容和人工审批触达验证。
- 目标客户类型：职业培训机构、人力资源服务公司、本地教育咨询团队。
- 小红书方向：证书适用人群科普、培训机构内容转化、HR 视角证书价值。
- 抖音方向：60 秒科普、招生误区、HR 合规视角。
- 跟进草稿：只生成不外发，强调人工确认。
- 待办：补充城市/证书类别/合规边界，收集公开竞品链接，生成草稿并人工确认。
- 风险：禁止包过、保就业、保收入、虚构案例；外部动作必须人工审批。

## 13. 失败点

失败分类：Cowork / Gateway 会话写权限门禁。

细节：

- Gateway health/status 成功。
- `sessions.create` 触发 `operator.write` scope upgrade。
- `device.pair.list/approve` 触发 `operator.pairing` scope upgrade。
- 未继续手工改 pairing 数据，避免绕过 OpenClaw 安全门禁。

## 14. 安全检查结果

- 未读取 `D:\OpenClaw\secrets`。
- 未输出真实 API Key。
- 未提交 API Key、Token、Cookie、日志、数据库、浏览器 Profile、node_modules、构建产物。
- 使用运行态 `gateway-token` 仅做本机 RPC 连接验证，未输出、未提交。
- 未真实外发邮件、私信、评论、帖子。
- 未连接真实社媒账号。
- 未安装官方专家套件远程 bundle。
- 测试结束后停止了本轮残留的 web-search bridge 进程。

## 15. 是否建议继续开发 domestic_signal_growth 真正版本

建议：继续，但先补一个明确的 Cowork UI/CLI 触发路径。

原因：

- LobsterAI + OpenClaw runtime 可用。
- DeepSeek V4 Pro 路由可用。
- 本地 Skill 接入路径可用。
- 当前唯一关键缺口是：自动化 E2E 需要通过 OpenClaw 本地设备权限审批或从 Electron UI 人工发起。

## 16. 结论

结论：B. 端到端部分成立，先修复 Cowork/CLI 写权限或 UI 触发阻塞点。

## 17. 下一步建议

1. 在 LobsterAI UI 中批准 CLI 的 `operator.write` / 必要 pairing scope，或设计一个只用于开发验证的受控本地调用入口。
2. 从 Cowork UI 手动发送本轮业务任务，观察模型回复、Skill 调用和 web-search 调用轨迹。
3. 如果 UI 内仍不能调用本地 Skill，再补最小 MCP/command bridge。
4. 进入 Phase 2 前，保留 `draft_only` 外部动作策略，不做任何自动发布/私信/评论/邮件。
