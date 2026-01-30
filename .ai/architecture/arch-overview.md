---
title: "Themis 项目架构概览"
version: "1.0.0"
last_updated: "2026-01-30"
status: "已批准"
---

## 1. 引言与目标 (Introduction & Goals)
本文档描述 Themis（敏感信息扫描工具）的高层架构，目标是提供**简单可用、易接入、性能友好**的扫描能力，并能在 `git commit` 与 GitLab CI 的 MR pipeline 中运行。

## 2. 架构原则 (Guiding Architectural Principles)
- 简单优先：少依赖、少模块、少层级。
- 可配置：按平台配置文件加载规则（`.themis.<platform>.yml`）。
- 性能优先：默认 diff 扫描、跳过大文件/二进制。
- 安全输出：默认脱敏，避免二次泄露。

## 3. 高层架构概览 (High-Level Architecture)
```
CLI (themis)
  ├─ Config Loader
  ├─ Scanner
  │    ├─ Rules Engine
  │    └─ Diff/Full Scanner
  └─ Reporter (text/json)
```

### 3.1 组件职责
- **CLI**：参数解析、模式选择（diff/full）、退出码控制。
- **Config Loader**：按 `--platform` 读取 `.themis.<platform>.yml`，无则回退默认（最小依赖）。
- **Scanner**：文件/行扫描，规则匹配，生成发现项。
- **Rules Engine**：执行 regex/关键词/熵规则（可开关高成本规则）。
- **Reporter**：脱敏并输出到 text/json。

## 4. 数据流 (Data Flow)
1. CLI 读取参数与配置  
2. Scanner 获取输入（diff or full；commit 默认 diff）  
3. Rules Engine 逐条评估并产出 findings  
4. Reporter 输出（脱敏）  
5. CLI 根据阈值设置退出码

## 5. 关键非功能性需求 (NFRs)
- **性能**：commit 仅 diff 扫描，避免全量遍历。
- **易用**：一键安装 hook，默认配置可用。
- **安全**：脱敏输出，避免日志泄露。

## 6. 目录结构建议 (Project Structure)
```
themis/
  cli.py
  config.py
  rules.py
  scanner.py
  report.py
tests/
```

## 7. 变更日志 (Change Log)
| 版本  | 日期       | 描述                     |
|------|-----------|--------------------------|
| 1.0.0| 2026-01-30 | 初版架构草稿              |
