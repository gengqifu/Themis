# v0.1.0 Release Notes

## 亮点
- 新增多平台配置模板（Android/iOS/Web/Backend），包含默认敏感信息规则。
- CLI 支持 `scan.block_on_severity`，可配置阻断阈值。
- 修复 diff-only 扫描在相对路径下无法命中的问题。
- 修复 zipapp 入口未传递退出码，确保 commit 阻断生效。
- README 补齐 commit/MR 快速上手、配置速查与排错指南。

## 变更明细
### 配置与规则
- 新增 `config-templates/` 平台配置模板目录。
- Android/iOS 模板补充平台特定敏感信息规则。

### CLI 与扫描
- CLI 退出码读取 `scan.block_on_severity`。
- 修复 diff-only 扫描路径对齐问题（绝对路径匹配）。
- 退出码解析更健壮（strip/大小写归一）。
- zipapp 入口更新为正确传递退出码。

### 文档
- README 新增 commit 阻断一条命令块、MR 片段、配置字段速查、常见问题。

## 升级说明
- 如使用 zipapp 分发，请重新打包并替换 `themis.pyz`。
- 使用 `scan.block_on_severity` 配置提交阻断阈值。
