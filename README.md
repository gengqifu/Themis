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
说明：不同平台请使用对应配置文件（`.themis.android.yml` / `.themis.ios.yml` / `.themis.backend.yml` / `.themis.web.yml`）。

## 快速开始（一条命令块：commit 阻断）
```
cp config-templates/.themis.android.yml ./.themis.android.yml
printf "scan:\n  block_on_severity: high\n" >> .themis.android.yml
python -m themis install-hooks --platform android --repo-root .
sed -i '' 's|themis scan|python3 ./themis.pyz scan|g' .git/hooks/pre-commit
```
说明：
- 若未使用 `themis.pyz`，可把 `themis` 放入 PATH，或跳过最后一行。
- commit 时命中阈值及以上会阻断提交。
- Android/iOS/Web/Backend 请分别使用对应的 `.themis.<platform>.yml` 配置文件。

## 快速开始（commit 阻断）
1) 复制平台配置模板到仓库根目录（示例 Android）：
```
cp config-templates/.themis.android.yml ./.themis.android.yml
```
2) 设置阻断阈值（默认只阻断 critical，改为 high）：
```yaml
scan:
  block_on_severity: high
```
3) 安装并确保 hook 可调用 themis：
- 安装：`python -m themis install-hooks --platform android --repo-root .`
- 方式 A（推荐）：把 `themis.pyz` 放入 PATH（或命名为 `themis`）
- 方式 B：修改 `.git/hooks/pre-commit` 中的命令为  
  `python3 ./themis.pyz scan ...`

提交时若命中阈值及以上严重程度，会阻断提交。

## 配置文件
- 平台默认配置文件命名：
  - `.themis.android.yml` / `.themis.ios.yml` / `.themis.backend.yml` / `.themis.web.yml`
- 配置模板（包含默认敏感信息规则集）：`config-templates/`
  - 不同平台需要使用各自的配置文件（Android/iOS/Web/Backend 分别对应各自文件）
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
- 优先使用 `CI_MERGE_REQUEST_DIFF_URL`（若存在，需启用 URL diff 读取）
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

简化步骤（GitLab MR）：
1) 复制平台配置文件到仓库根目录（例如 `.themis.backend.yml`）
2) 配置 CI/CD Variables：`GITLAB_TOKEN`
3) 在 `.gitlab-ci.yml` 中调用 MR 集成入口（见示例文件）

最小可用片段（MR 回写 discussion）：
```yaml
script:
  - |
    python3 - <<'PY'
    import sys
    from themis.mr_integration import run_mr_scan_job_safe

    sys.exit(
        run_mr_scan_job_safe(
            platform="backend",
            paths=["."],
            repo_root=".",
        )
    )
    PY
```

Runner 配置检测流程（一步到位）：
1) 打开项目页面 → Settings → CI/CD → Runners，确认已有可用 Runner（状态为 online）。
2) Runner executor 选择 `docker`，并可拉取镜像（建议 `python:3.12`）。
3) 在 CI/CD Variables 配置 `GITLAB_TOKEN`（具备创建 MR discussion 权限）。
4) 设置 `GIT_DEPTH: "0"`，避免 `no merge base`。
5) 提交一个 MR，触发 pipeline，在 Job 日志里确认：
   - 成功拉取仓库代码；
   - 能访问 GitLab API（无 4xx/5xx 报错）；
   - MR diff 获取成功。
6) 若无 discussion：
   - 确认使用 `mr_integration` 入口；
   - 确认 `GITLAB_TOKEN` 权限与 scope；
   - 确认 Runner 能访问 `CI_API_V4_URL`。

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
- `2`：命中（默认阻断阈值为 critical，可配置 `scan.block_on_severity`）
- `1`：运行失败（例如 diff 解析/扫描异常）

## 配置字段速查
- `scan.mode`: `diff|full`
- `scan.block_on_severity`: `low|medium|high|critical`
- `scan.max_file_size_bytes`: 单文件大小阈值
- `rules`: 规则列表（`id/severity/type/pattern/message/enabled`）
- `allowlist`: `paths/regexes/line_markers`
- `output`: `format/redact_keep`

## 规则编写与使用
规则示例（regex 类型）：
```yaml
rules:
  - id: GOOGLE_API_KEY
    severity: high
    type: regex
    pattern: "AIza[0-9A-Za-z-_]{35}"
    message: "Possible Google API key"
    enabled: true
```

字段说明：
- `id`: 规则唯一标识（建议全大写或驼峰）
- `severity`: 严重程度（`low|medium|high|critical`）
- `type`: 规则类型（当前仅支持 `regex`）
- `pattern`: 正则表达式（按行匹配）
- `message`: 命中提示信息
- `enabled`: 是否启用（默认 true）

规则使用方法：
1) 在仓库根目录放置 `.themis.<platform>.yml`
2) 将 `rules` 写入配置文件（可覆盖默认规则集）
3) 运行 `themis scan ...` 或提交触发 hook

规则文件位置建议：
- 建议每个平台使用独立配置文件（Android/iOS/Web/Backend）
- 如需共享规则，可复制模板后在各平台配置中同步更新

## 常见问题
- **commit 不阻断**：确认 `.git/hooks/pre-commit` 可执行、命令指向正确的 `themis` 或 `themis.pyz`，并且 staged diff 中包含命中行。
- **diff 模式无命中**：确认使用 `git add` 后的 staged diff，或改用 `--diff-file`。
- **MR 无 discussion**：确认使用 `mr_integration` 入口，并配置 `GITLAB_TOKEN` 权限。

## 安全提示
- 默认输出脱敏，避免在日志中泄露完整敏感信息。
