# 验收标准

## 工程验收

- `domestic_signal_growth` 能直接调用。
- `search_adapter` 能返回公开来源或明确 `unverified/search_failed`。
- 三个制造业测试任务均能生成结构化 JSON。
- 所有输出保持 `draft_only`。
- 不读取 secrets，不真实外发。

## UI 鼠标验收

至少 2 个测试任务必须通过普通用户 UI 路径：

- UI 能正常发送。
- UI 不出现 gateway timeout。
- UI 显示结构化结果。
- 结果包含产品理解、商机发掘、宣传物料、评论/私信草稿、账号养成计划、工厂对接单。
- 结果保持 `draft_only`。
- 没有真实外发。

## 结论规则

- A：至少 2 个任务通过 UI 鼠标验收，且工程验收通过。
- B：工程验收通过但 UI 部分存在明确问题。
- C：UI 真实路径不成立，需要暂停功能扩展。
