# 宇智能 GitHub 发布准备清单

## 仓库

- GitHub 仓库 URL：https://github.com/zemumu133/yuzhineng
- 本地 remote 名称：`github-yuzhineng`
- 当前本地分支：`merge-growth-os-cleanroom`
- 推荐推送分支：`main` 或 `v2-open-source-growth-system`

## 当前推送状态

2026-07-03 已按用户确认，将当前分支 `merge-growth-os-cleanroom` 推送到：

```text
https://github.com/zemumu133/yuzhineng/tree/merge-growth-os-cleanroom
```

本次推送前已完成 `v2-task-postcheck.ps1`，未提交 secrets、logs、database、backups、data、exports、browser profile、node_modules、构建产物或真实项目成果。

当前仍不建议创建正式 release/tag。正式 release 应等待 PACK-1 可移植安装包 PoC 和干净机恢复验证完成。

## 推送前必须完成

1. LobsterAI 补丁固化：如果修改上游源码，必须导出到 `D:\OpenClaw\v2\vendor-patches\lobsterai\`。
2. 不提交 `node_modules/`、`dist/`、`build/`、缓存目录和构建产物。
3. 不提交 `secrets/`、`.env`、API Key、Token、Cookie、浏览器 Profile。
4. 不提交 `D:\OpenClaw\v2\projects` 中的真实项目运行数据。
5. 不提交 `logs/`、`database/`、`backups/`、`data/`、`exports/`。
6. 打包脚本需要先完成本机验证和干净机安装验证。
7. 确认 `advanced_auto_mode`、真实发布、真实评论、真实私信、真实邮件功能默认关闭。
8. 确认 Growth OS 的 ActionIntent 和 approval queue 默认 `draft_only` 或 `approval_required`。
9. 确认开源许可证和上游版权声明没有被删除。

## 建议发布流程

1. 先提交宇智能主线代码、配置模板、文档、测试和可复现 patch。
2. 再执行一次 `v2-task-postcheck.ps1` 和完整测试。
3. 检查 `git status --ignored`，确认运行数据被忽略。
4. 推送代码分支到 `github-yuzhineng`。
5. 打包验证通过后再创建 release/tag。

## 禁止进入 GitHub 的路径和内容

- `D:\OpenClaw\secrets`
- `D:\OpenClaw\logs`
- `D:\OpenClaw\database`
- `D:\OpenClaw\backups`
- `D:\OpenClaw\data`
- `D:\OpenClaw\browser_profiles`
- `D:\OpenClaw\v2\projects` 真实项目成果
- `node_modules`
- 构建产物、缓存、截图大文件、真实运行日志
- API Key、Token、Cookie、浏览器 Profile、真实社媒账号信息

## 后续建议

继续完成 PACK-1 可移植安装包 PoC，并生成一次“干净机恢复清单”，确保新设备只靠仓库代码、配置模板、patch 和安装脚本即可还原开发环境，不依赖本机隐藏状态。
