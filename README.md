# Themis
用于扫描代码中的潜在敏感信息与安全隐患。

## 运行环境
- Python 3.10+
- 依赖安装：`pip install -r requirements.txt`

## 单文件可执行（zipapp）
适合不想使用 venv 的场景。只需系统已有 `python3`。

构建（开发者/CI 侧）：
```
./bin/build-zipapp.sh
```
说明：脚本会在 `build/` 下创建临时 venv 安装依赖，不会污染系统 Python。

产物：
- `dist/themis.pyz`

使用：
- `python3 dist/themis.pyz scan . --platform backend`
- 或放入 PATH 后：`themis.pyz scan . --platform backend`

## 快速开始（本地扫描）
- 扫描当前目录（默认规则）：`python -m themis scan . --platform backend`
- JSON 输出：`python -m themis scan . --platform backend --format json`

## 配置文件
- 平台默认配置文件命名：
  - `.themis.android.yml` / `.themis.ios.yml` / `.themis.backend.yml` / `.themis.web.yml`
- 可选字段（顶层）：`scan` / `rules` / `allowlist` / `baseline` / `output`
- 示例（最小可用）：
  ```yaml
  scan:
    mode: diff
  output:
    format: text
  allowlist:
    line_markers:
      - themis:ignore
  ```

## diff 扫描
当 `scan.mode: diff`：
- 优先使用 `CI_MERGE_REQUEST_DIFF_URL`（若存在）
- 或使用 `--diff-file` 指定统一 diff 文件

示例：
`python -m themis scan . --platform backend --diff-file /path/to/diff.patch`

## 本地 commit hook
- 安装：
  - `python -m themis install-hooks --platform backend --repo-root .`
- 卸载：
  - `python -m themis uninstall-hooks --repo-root .`

## GitLab MR 集成示例
- 参考 `.gitlab-ci.yml.example`，可在 `merge_request_event` 时触发扫描并回写同一条 discussion。
- 示例默认使用 `backend` 平台配置，可按仓库类型改为 `android` / `ios` / `web`。

必需环境变量（在 GitLab CI/CD Variables 配置）：
- `GITLAB_TOKEN`（建议使用 masked + protected，最小权限）
- `CI_PROJECT_ID`
- `CI_MERGE_REQUEST_IID`
- `CI_API_V4_URL`

说明：
- `CI_PROJECT_ID`、`CI_MERGE_REQUEST_IID`、`CI_API_V4_URL` 由 GitLab CI 自动注入。
- `GITLAB_TOKEN` 需手动在仓库或组级变量中配置。

## 退出码（scan）
- `0`：未命中
- `2`：命中（阻断阈值为 critical）
- `1`：运行失败（例如 diff 解析/扫描异常）
