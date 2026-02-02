---
title: "SS003 - GitLab MR 集成（回写 review comment/讨论）"
id: "SS003"
target_version: "v0.2"
status: "已批准"
owner: "AI 助手"
story_points: "TBD"
jira_id: ""
created_date: "2026-01-29"
last_updated: "2026-02-02"
related_prd_feature: "../index.md"
---

## 1. 用户故事描述 (User Story Description)
**作为一个** 代码仓库管理员/安全负责人  
**我想要** 使用 GitLab CI 在 Merge Request 创建/更新时触发扫描，并把结果以 review comment/讨论的形式回写到 MR  
**以便于** 让 reviewer 看到明确的风险与建议（当前不阻断合并）

## 2. 验收标准 (Acceptance Criteria - AC)
- [ ] AC1: 使用 GitLab CI 的 MR pipeline 触发扫描（opened/updated），`.gitlab-ci.yml` 中通过 `merge_request_event` 规则触发
- [ ] AC2: 获取 MR diff 并使用 `diff` 模式扫描（优先 CI 提供的 diff；缺失时回退 GitLab API；都失败则任务失败并输出错误）
- [ ] AC3: 将扫描结果回写到 MR 的 **discussion**（仅 discussion），并通过固定锚点（例如 `<!-- themis:mr-scan -->`）更新同一条 discussion，避免重复创建
- [ ] AC4: 回写内容默认脱敏，避免泄露（不写入完整 secret）；默认前后保留 2 字符，中间 `***`
- [ ] AC4.1: 单次回写条数上限可配置（默认 50）；超限时输出摘要（总数 + 前 N 条）
- [ ] AC5: 兼容 GitLab self-managed 13.5.3（相关 API endpoint/字段经过该版本验证）
- [ ] AC6: CI 必需环境变量明确并校验（至少：`CI_PROJECT_ID`、`CI_MERGE_REQUEST_IID`、`CI_API_V4_URL`、`GITLAB_TOKEN`）
- [ ] AC7: 任务失败退出码统一为非 0，并在日志输出错误类型（变量缺失/API 失败/网络异常）

## 3. 背景与上下文 (Context & Background)
- 使用 GitLab CI 在 MR 阶段触发扫描；当前未开通“阻断 MR 合并”的能力，因此本 Story 的目标是“回写 comment/讨论”，不做阻断。

## 4. 技术设计与实现计划 (Technical Design & Implementation Plan)

### 4.1. 提议的解决方案/方法 (Proposed Solution / Approach)
候选集成方式（已确定使用 GitLab CI）：
- 在 CI job 中运行 `themis scan --diff`（基于 CI 提供的 MR diff 信息或 API 拉取）
- 使用 GitLab API 回写 MR discussion（固定更新同一条 discussion，避免重复）

### 4.2. 安全性考量
- GitLab token 权限最小化：只需读取 MR diff + 写入 MR 评论/状态
- 扫描结果脱敏与限量（避免刷屏与二次泄露）

## 5. 任务 (TDD 聚焦) (Tasks (TDD Focused))
- [x] 1. **测试**：MR pipeline 变量解析与 diff 获取逻辑
- [x] 2. **测试**：discussion 回写（更新同一条 discussion）
- [x] 3. **测试**：CI 运行输出（脱敏、格式正确）
- [x] 4. **测试**：异常路径（API 失败/权限不足/网络异常/diff 为空）
- [x] 4. **实现**：CI job 触发条件与必要变量（MR pipeline）
- [x] 5. **实现**：GitLab API 客户端（获取 MR diff、回写 discussion）
- [x] 6. **实现**：集成扫描器并生成 MR 友好的输出
- [x] 7. **实现**：discussion 锚点机制（固定更新同一条 discussion）
- [x] 8. **实现**：`.gitlab-ci.yml` 集成样例与必需环境变量说明
- [x] 9. **重构**：抽离 CI/MR 适配层，减少耦合
- [ ] 10. **测试**：端到端（本地模拟 CI 环境 + mock GitLab API）
- [ ] 11. **实现**：统一失败退出码与错误分类输出

## 6. 待解决问题 (Open Questions)
- GitLab 为 self-managed，版本 13.5.3。
- discussion 的更新策略：更新同一条 discussion。

## 7. 图表 (可选) (Diagrams (Optional))
（无）

## 8. 开发笔记与日志 (Development Notes & Log)
- 2026-01-29 - AI: Story 草稿，按“GitLab CI 触发 + MR 评论回写、不阻断合并”的方案整理。
- 2026-02-02 - AI: 完成任务 5.1，新增 `tests/test_ci_context.py`（CI 变量解析、diff 来源优先级）与 `themis/ci_context.py` 最小实现，验证通过定向测试。
- 2026-02-02 - AI: 完成任务 5.2，新增 `tests/test_gitlab_mr_discussion.py`，覆盖“命中锚点更新同一条 discussion / 未命中则新建 discussion”两个核心场景（TDD 红阶段）。
- 2026-02-02 - AI: 完成任务 5.3，新增 `tests/test_gitlab_mr_output.py`，覆盖 CI 输出脱敏、字段格式与条数上限摘要（TDD 红阶段）。
- 2026-02-02 - AI: 完成任务 5.4，新增 `tests/test_gitlab_mr_errors.py`，覆盖 API 失败/权限不足/网络异常分类与空 diff 拒绝（TDD 红阶段）。
- 2026-02-02 - AI: 完成任务 5.4（实现），在 `themis/ci_context.py` 增加 MR pipeline 来源判断与守卫（`merge_request_event`），并补充对应单测。
- 2026-02-02 - AI: 完成任务 5.5，实现 `themis/gitlab_mr.py`（GitLab API 客户端、MR diff 获取、discussion upsert、输出格式化与错误分类），并使 5.2~5.4 相关测试转绿。
- 2026-02-02 - AI: 完成任务 5.6，新增 `build_mr_scan_output` 把 diff 行过滤扫描与 MR discussion 输出串联，并新增 `tests/test_gitlab_mr_scan.py` 验证脱敏与 diff 命中。
- 2026-02-02 - AI: 完成任务 5.7，确认并固化 discussion 锚点更新机制（`DISCUSSION_ANCHOR` + `upsert_scan_discussion`），同条 discussion 更新行为通过测试。
- 2026-02-02 - AI: 完成任务 5.8，新增 `.gitlab-ci.yml.example`（MR pipeline 触发、回写 discussion）并在 `README.md` 补充必需环境变量说明。
- 2026-02-02 - AI: 完成任务 5.9，新增 `themis/mr_integration.py` 抽离 MR 扫描编排层（环境解析、API 客户端、扫描与回写），并将 `.gitlab-ci.yml.example` 改为调用单一入口以降低耦合；新增 `tests/test_mr_integration.py`。

## 9. AI 交互日志 (Chat Command Log - AI Interaction Record)
- 用户: GitLab 为 self-managed；MR 使用 GitLab CI 触发扫描；回写方式仅 discussion；不阻断合并；commit 阶段仅 critical 阻断；多仓多平台各平台独立配置文件；输出默认脱敏且可配置开关。
- 用户: 执行 SS003 任务 5.1（MR pipeline 变量解析与 diff 获取逻辑）。
- 用户: 执行 SS003 任务 5.2（discussion 回写与同条更新测试）。
- 用户: 执行 SS003 任务 5.3（CI 输出脱敏与格式测试）。
- 用户: 执行 SS003 任务 5.4（异常路径测试：API/权限/网络/空 diff）。
- 用户: 执行 SS003 任务 5.4（实现：MR pipeline 触发条件与必要变量）。
- 用户: 执行 SS003 任务 5.5（实现 GitLab API 客户端）。
- 用户: 执行 SS003 任务 5.6（集成扫描器并生成 MR 输出）。
- 用户: 执行 SS003 任务 5.7（discussion 锚点机制实现）。
- 用户: 执行 SS003 任务 5.8（`.gitlab-ci.yml` 集成样例与变量说明）。
- 用户: 执行 SS003 任务 5.9（抽离 CI/MR 适配层，减少耦合）。
