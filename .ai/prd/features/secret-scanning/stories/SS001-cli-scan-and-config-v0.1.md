---
title: "SS001 - CLI 扫描与规则/配置加载"
id: "SS001"
target_version: "v0.1"
status: "已批准"
owner: "AI 助手"
story_points: "TBD"
jira_id: ""
created_date: "2026-01-29"
last_updated: "2026-01-29"
related_prd_feature: "../index.md"
---

## 1. 用户故事描述 (User Story Description)
**作为一个** 开发者/安全负责人  
**我想要** 在本地或自动化环境中运行一个 `python3` CLI 工具扫描仓库中的敏感信息  
**以便于** 在代码合并前发现并处理潜在泄露

## 2. 验收标准 (Acceptance Criteria - AC)
- [ ] AC1: 提供 CLI 入口 `themis scan`（兼容 `python -m themis scan`），支持指定扫描路径/文件列表；未指定路径时默认扫描当前工作目录
- [ ] AC2: 配置查找顺序：`--config` > `--platform`(`.themis.<platform>.yml`) > 内置默认
- [ ] AC2.1: 零配置可用：当配置文件不存在时，仍可使用内置默认规则运行（开箱即用）
- [ ] AC3: 输出格式支持 `text` 与 `json`（可选）；`json` 输出最小结构为 `{ "findings": [...] }`，每个 finding 至少包含 `rule_id/severity/file/line/message`
- [ ] AC4: 脱敏策略：默认仅展示命中前后各 2 个字符（可配置），中间用 `***` 替代
- [ ] AC5: 退出码约定：`0`=成功且未达阻断阈值；`2`=达到阻断阈值（用于 git hook 阻断）；`1`=运行错误
- [ ] AC6: 提供快速扫描默认值以适配 `git commit`：支持只扫 diff 输入、跳过二进制/超大文件，并默认关闭高成本规则：`entropy`（字符串熵检测）、`generic_high_entropy`（无前缀的高随机度 token/长串检测）。

## 3. 背景与上下文 (Context & Background)
- 目标是全栈适配（Android/Backend/Web/iOS），因此扫描器应以“文本 + 规则”为核心，避免与具体语言绑定。
- 你希望输出所有扫描到的敏感信息，但为避免二次泄露，默认应脱敏；允许输出原文通过配置开关控制（仅限受控环境）。
- 本阶段需要支持在 `git commit` 阶段阻断提交，因此 CLI 必须支持“按严重程度阈值决定退出码（默认仅 `critical` 阻断）”。

## 4. 技术设计与实现计划 (Technical Design & Implementation Plan)

### 4.1. 提议的解决方案/方法 (Proposed Solution / Approach)
- Python 包结构：
  - `themis/cli.py`：命令行解析与主流程
  - `themis/config.py`：配置加载与校验
  - `themis/scanner.py`：文件遍历与规则执行
  - `themis/rules.py`：规则模型与匹配逻辑
  - `themis/report.py`：结果格式化（text/json）
- 配置解析：优先支持 YAML（若不引入依赖，可退化为 JSON），按 `--platform` 查找平台配置文件（`.themis.<platform>.yml`），并提供默认内置规则集。
- 文件读取：以 UTF-8 为主，容错处理编码错误；跳过二进制与超大文件（由配置控制）。
- 性能：为 `git commit` 提供快速路径（diff-only + 轻量规则优先），避免明显拖慢提交。

### 4.2. 关键组件/模块影响 (Key Components / Modules Affected)
- CLI：参数、默认配置路径、错误处理
- Config：配置 schema、默认值、合并规则
- Scanner：文件发现、过滤、逐行扫描、定位行号
- Report：脱敏与输出格式

### 4.3. 潜在风险与缓解 (Potential Risks & Mitigation)
- 误报：先做“高置信度”规则集 + allowlist/baseline（由 SS002 承接）
- 性能：限制文件大小、并可选只扫 diff（由 SS002 承接）
- 二次泄露：默认脱敏与截断；敏感片段不写入日志

## 5. 任务 (TDD 聚焦) (Tasks (TDD Focused))
- [ ] 建立 Python 包骨架与 CLI 入口（最小可运行）
- [ ] 编写配置加载测试（默认路径/参数覆盖/错误提示）
- [ ] 实现配置加载与 schema 校验
- [ ] 编写扫描器核心测试（规则匹配 -> 命中；行号定位正确）
- [ ] 实现逐文件/逐行扫描与结果结构
- [ ] 编写输出格式测试（text/json；脱敏默认前后 2 字符）
- [ ] 编写退出码测试（0/1/2 对应成功/错误/阻断）
- [ ] 更新 Story 的 Development Notes & Log

## 6. 约束与依赖关系 (Constraints & Dependencies)
- 约束：commit 阶段必须快速（diff-only、跳过大文件/二进制）
- 依赖：无

## 7. 图表 (可选) (Diagrams (Optional))
（无）

## 8. 开发笔记与日志 (Development Notes & Log)
- 2026-01-29 - AI: 初始化 Story 草稿，待用户确认配置格式与输出脱敏策略细节。

## 9. AI 交互日志 (Chat Command Log - AI Interaction Record)
- 用户: MR 使用 GitLab CI 触发扫描并回写评论（不阻断合并）；commit 阶段仅 `critical` 阻断；多仓多平台，每个平台独立配置文件（`.themis.<platform>.yml`）；输出默认脱敏，配置开关可调整。
