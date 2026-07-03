# 宇智能项目成果迁移说明

## 1. projects 目录是什么

`D:\OpenClaw\v2\projects\` 保存真实项目成果，包括产品资料卡、推广方案、客户交接单、待办、安全检查和索引页。

## 2. 为什么不提交 Git

`projects` 目录属于本机运行数据，可能包含客户资料、业务草稿和内部交接内容，因此已被 `.gitignore` 排除，不会提交到 Git。

## 3. 换设备时怎么迁移

换设备时必须整体复制：

`D:\OpenClaw\v2\projects\`

至少要包含：

- `projects_index.json`
- `index.html`
- 每个项目目录
- 每个项目目录内的 `product_profile.json`
- 每个项目目录内的 `product_card.md`
- 每个项目目录内的 `report.md`
- 每个项目目录内的 `handoff.docx`
- 每个项目目录内的 `todos.json`

## 4. 不要混入这些内容

迁移 projects 时不要混入：

- API Key
- Token
- Cookie
- 浏览器 Profile
- logs
- secrets
- node_modules
- 临时缓存

## 5. 当前阶段限制

当前只提供人工复制迁移说明，不做复杂同步系统。

后续可以增加：

- 项目导出 zip
- 项目导入工具
- 脱敏导出
- 按客户/项目筛选导出
