# 宇智能 Growth OS 数据获取层

本目录提供真实数据获取层的基础框架。Phase M1 只实现安全的结构和沙盒数据流，不接真实 API Key，不登录平台，不绕验证码，不采集私人联系方式。

## 当前可用

- 人工导入公开 URL。
- 公开网页搜索结果的来源证据建模。
- 沙盒 CSV / 沙盒公司线索生成。
- Evidence 与 Lead 的标准字段。

## 安全边界

- 没有来源的线索必须标记为 `unverified`。
- 没有公开联系方式时 `contact_status = unknown`。
- 任何触达建议必须转成 ActionIntent 并进入审批队列。

