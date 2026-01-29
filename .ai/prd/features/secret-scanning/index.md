---
title: "Feature (特性) PRD: Secret & Sensitive Info Scanning（敏感信息扫描）"
version: 1.0.0
feature_id: "secret-scanning"
last_updated: 2026-01-29
jira_id: ""
owner: "{待补充}"
status: "已批准"
---

## 1. 引言与目的 (Introduction & Purpose)
在 `git commit` 与 Merge Request 阶段对变更内容进行敏感信息扫描，重点覆盖 Google Play/GCP 相关 key（commit 阶段严重命中需阻断提交），同时支持用户名/密码/token 等敏感信息检测；规则与豁免策略可配置，适配 Android/Backend/Web/iOS 等全栈仓库。

## 2. 目标与宗旨 (Goals & Objectives)
- 默认模式：扫描 MR diff（新增/修改行），输出所有命中（默认脱敏）。
- 可选模式：支持全量扫描开关（对指定目录或整个仓库）。
- 阻断策略：在 `git commit` 阶段对严重命中进行阻断提交（默认仅 `critical`）。
- MR 策略：当前仅回写 review comment/讨论，不阻断 MR 合并。
- 规则与豁免均配置化：支持路径忽略、行内注释忽略、baseline。
- 多仓多平台适配：每个平台使用独立配置文件，并提供对应平台的默认规则集。

## 3. 范围 (Scope)
### 3.1. 范围内 (In Scope)
- 扫描引擎：文本文件扫描、规则匹配（regex/关键字 + 熵阈值）、结果聚合与去重
- 配置系统：规则集 + allowlist（路径/注释/baseline）
- 扫描模式：`diff` 默认 + `full` 可选
- 输出：`text` + `json`（至少一种机器可读格式）
- GitLab Merge Request 集成（不依赖 AI；MR 事件触发扫描并回写结果为评论/讨论；不阻断）
- Git hooks 集成：在 `git commit` 阶段运行扫描并在严重命中时阻断提交

### 3.2. 范围外 (Out of Scope)
- 扫描 Git 历史全量泄露（可作为未来增强）
- 自动修复/自动轮转密钥

## 4. 功能性需求与用户故事 (Functional Requirements & User Stories)

### 4.1. Story: SS001 - CLI 扫描与规则/配置加载
- **描述**: 提供 `python3` CLI，可对指定目录或指定文件列表运行扫描，加载规则与豁免配置，并输出结果。
- **状态**: 草稿
- **目标版本**: v0.1
- **详细故事文档**: [./stories/SS001-cli-scan-and-config-v0.1.md](./stories/SS001-cli-scan-and-config-v0.1.md)

### 4.2. Story: SS002 - Diff/Full 扫描模式与 baseline/注释豁免
- **描述**: 默认只扫描 MR diff（或给定 diff 输入），支持全量扫描开关；支持 baseline、路径与行内注释豁免。
- **状态**: 草稿
- **目标版本**: v0.1
- **详细故事文档**: [./stories/SS002-diff-full-and-exemptions-v0.1.md](./stories/SS002-diff-full-and-exemptions-v0.1.md)

### 4.3. Story: SS003 - GitLab MR 集成（回写 review comment/讨论）
- **描述**: MR 事件触发扫描、回写结果到 review comment/讨论（当前不阻断合并）。
- **状态**: 草稿
- **目标版本**: v0.2
- **详细故事文档**: [./stories/SS003-gitlab-mr-integration-v0.2.md](./stories/SS003-gitlab-mr-integration-v0.2.md)

### 4.4. Story: SS004 - Git commit 阶段阻断（Git hook）
- **描述**: 提供可安装/可复用的 git hook（或安装命令），在 `git commit` 时运行扫描并在严重命中时阻断提交。
- **状态**: 草稿
- **目标版本**: v0.1
- **详细故事文档**: [./stories/SS004-git-commit-hook-blocking-v0.1.md](./stories/SS004-git-commit-hook-blocking-v0.1.md)

## 5. 非功能性需求 (此特性专属) (Non-Functional Requirements)
- 性能（commit 阶段优先）：默认只扫描 staged diff（新增/修改行），避免全仓库遍历；对大文件/二进制直接跳过；确保不会明显拖慢提交（待量化）
- 性能（MR 阶段）：diff 扫描对常见 MR 规模应在可接受时间内完成（待量化）
- 安全：输出默认脱敏，避免把真实 secret 写入日志/MR 评论
- 可维护性：规则集可版本化，并能用样本集进行回归验证
- 简单性：控制代码规模与模块数量，避免过度抽象；提供开箱即用的默认配置与“一键接入”方式（例如安装 git hook 的单条命令）

## 6. 配置文件建议（草案）
多仓多平台场景建议“每个平台独立配置文件”，例如：
- Android: `.themis.android.yml`
- iOS: `.themis.ios.yml`
- Backend: `.themis.backend.yml`
- Web: `.themis.web.yml`

每个平台配置文件结构保持一致：
- `scan`: `mode`（`diff|full`）、`max_file_size_bytes`、`include_globs`、`exclude_globs`
- `rules`: 规则列表（`id`、`category`、`severity`、`type`、`patterns`、`entropy_threshold`、`keywords`、`message`）
- `allowlist`: `paths`、`regexes`、`line_markers`（行内注释忽略）
- `baseline`: 指向 baseline 文件路径（用于忽略已知历史命中）
- `output`: `format`（`text|json`）、`redact`（是否脱敏）、`max_findings`

CLI 参数：
- `--platform android|ios|backend|web`
- 可选 `--config` 显式指定配置文件路径
默认策略：优先按 `--platform` 查找平台配置文件；未找到则回退到内置默认规则集（确保零配置可用）。

## 7. 默认敏感信息范围建议（草案）
- **Critical（建议阻断）**:
  - Google Play/GCP：Service Account JSON（`type: service_account` + `private_key` + `client_email` 等组合特征）
  - 私钥/证书：`BEGIN ... PRIVATE KEY`，以及常见 keystore/p12 文件（是否阻断取决于团队策略）
  - 常见高价值 token（可逐步补齐规则库）
- **High（建议强告警或阻断）**:
  - 云厂商 access key + secret 组合（可做结构校验）
  - 含密码的数据库连接串
- **Medium/Low（默认告警）**:
  - `username/password` 等弱模式（建议关键词 + 结构 + 熵阈值，避免误报）

## 8. 待解决问题与假设 (Open Questions & Assumptions)
- “Google Play 的 key”具体类型：打包用的 `keystore`（签名密钥/证书相关）。
- CI/MR 集成方式：使用 GitLab CI 在 Merge Request 阶段触发扫描并回写 review comment/讨论（当前不阻断合并）。
- `git commit` 阶段阻断方式：优先支持“仓库内一键安装 hook”（统一接入）；若无法可靠统一，则退化为开发者本机手动配置（次选）。
- 输出策略：提供配置开关（默认脱敏输出；在受控环境/本地可选输出更多细节）。
- 严重命中阈值：默认仅 `critical` 阻断 commit。
