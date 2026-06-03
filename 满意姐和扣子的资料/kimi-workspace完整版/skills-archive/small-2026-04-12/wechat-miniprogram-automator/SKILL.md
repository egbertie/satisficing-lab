---
name: wechat-miniprogram-automator
description: Automate WeChat Mini Program DevTools from the terminal with `miniprogram-automator`. Use when harness engineering needs repeatable Mini Program flows such as launching or connecting to DevTools, re-launching routes, tapping selectors, filling inputs, collecting page data, mocking `wx` methods, or capturing screenshots during debugging and smoke checks.
---

# WeChat Mini Program Automator

Drive WeChat Mini Program DevTools through `miniprogram-automator` instead of ad hoc UI clicking. Prefer the bundled runner for stable, JSON-driven harness workflows.

## Prerequisite check

Before running any workflow, verify all of the following:

```bash
command -v node >/dev/null 2>&1
test -x /Applications/wechatwebdevtools.app/Contents/MacOS/cli || true
node -p "require.resolve('miniprogram-automator')"
```

If `require.resolve` fails, install the package in the working directory:

```bash
npm install miniprogram-automator
```

If connecting to an already-open DevTools window, ensure the target project is open with automation enabled. The package reports connection failures as "check if target project window is opened with automation enabled".

## Skill path

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export WXA_RUNNER="$CODEX_HOME/skills/wechat-miniprogram-automator/scripts/run_automator.cjs"
export WXA_RESOLVER="$CODEX_HOME/skills/wechat-miniprogram-automator/scripts/resolve_wechat_project.cjs"
export WXA_BOOTSTRAP="$CODEX_HOME/skills/wechat-miniprogram-automator/scripts/ensure_devtools_session.cjs"
export WXA_FLOW="$CODEX_HOME/skills/wechat-miniprogram-automator/scripts/run_wechat_flow.cjs"
export WXA_BATCH="$CODEX_HOME/skills/wechat-miniprogram-automator/scripts/run_wechat_batch.cjs"
```

## Preferred workflow

1. Resolve the current repo first. Do not assume the working directory is itself the DevTools project root.
2. If the resolver returns multiple hosted targets, present the candidate hosts to the user and ask them to choose before continuing.
3. Prefer `cli auto` bootstrapping plus `connect`, even when you know the project path.
4. Use `launch` only as a fallback for clean, disposable sessions where the project is not already open in DevTools.
5. Store the interaction plan as JSON in a temporary file instead of embedding long action arrays directly in the prompt.
6. Run the bundled script and inspect its JSON output.
7. Save screenshots or other artifacts under `output/wechat-miniprogram-automator/` when the repo already has an output area. Otherwise use `/tmp`.
8. For multi-page smoke checks, prefer `run_wechat_batch.cjs` so the batch leaves one top-level `report.json` plus one subreport per case.
9. On Taro React pages, prefer adding `root` or `inspectDataTree` when you need structure-level snapshots. Business hook state such as `loading` or `houseData` may resolve to `undefined` from `page.data(path)`.
10. Before a long batch, prefer a short canary or preflight flow that proves the page has moved beyond loading or skeleton state.

Readiness selector guidance:

- `container selector`: the page shell, root node, list wrapper, or layout block that can appear before real content is ready
- `business selector`: the first selector that only appears after real data has rendered, such as the first card, the real title text block, an image inside a swiper, or an enabled submit button
- For preflight and smoke checks, prefer `business selector` over `container selector`
- If the page can render a skeleton immediately, do not use only the route root as the final readiness condition

## Resolve project shape first

Use the resolver before picking `launch` or `connect`:

```bash
node "$WXA_RESOLVER" --cwd "$PWD"
```

The resolver returns one of these shapes:

- `standalone-miniprogram`: the current repo is itself the Mini Program root. Use `projectPath` directly.
- `hosted-subpackage`: the current repo builds into one or more host Mini Programs. Use `selectedTarget.devtoolsProjectPath` as the DevTools project path, not the current repo path.
- `unknown`: the skill could not find either shape and needs manual input.

For hosted subpackages, the resolver inspects `package.json`, `.mps.config.js`, and `config/index.js`, then returns structured target metadata such as:

- `weappType`: internal build target such as `tongcheng` or `wuba`
- `scriptSuffix`: script-facing short name such as `wbfc` or `ajk`
- `publishKey`: script-facing target such as `weapp-wbfc`
- `devScript`: watch command to keep the subpackage output synced into the host
- `hostProjectPath`: runtime Mini Program root that contains `app.json`
- `devtoolsProjectPath`: DevTools project root that contains `project.config.json`
- `subpackageRoot`: relative path from the host root to the mounted subpackage output
- `isActiveCandidate`: whether the resolver found a matching running watch process
- `selectionReason`: why the target was marked active or recommended

`--target` accepts any of `weappType`, `scriptSuffix`, `publishKey`, or full script names such as `dev:weapp-wbfc`.

This split matters because some hosts keep `project.config.json` one level above the runtime `miniprogram/` directory. Opening the runtime root in DevTools can start a broken or partial session even though the files exist.

## Ask the user to choose the host

When the resolver returns more than one hosted target, do not silently pick one and continue.

Instead:

1. Summarize the candidate hosts in plain language.
2. Include enough fields for the user to recognize the right target:
   - `weappType`
   - `devScript`
   - `devtoolsProjectPath`
   - `subpackageRoot`
3. Ask the user to choose one target.
4. Only continue with bootstrap, connect, route changes, or screenshots after the user has picked the target.

Use the resolver default only when there is exactly one hosted target.

When the resolver can uniquely match a running `dev:weapp-*` or `taro build --watch` process, it also returns `recommendedTarget`. Use that recommendation to prefill or highlight the likely host, but still ask the user to confirm when multiple hosts exist.

## Bootstrap DevTools first

Prefer this over `automator.launch()`:

```bash
node "$WXA_BOOTSTRAP" --project-path /abs/path/to/devtools-project
```

Internally this runs `cli auto --project ... --auto-port <port>`. If you call bootstrap directly, you can still manage a fixed port yourself. If you use the higher-level `flow` or `batch` entrypoints, they now derive a stable per-project port from `devtoolsProjectPath` so different projects do not accidentally reuse the same old session. That flow is idempotent enough for day-to-day use:

- if the project is already open, DevTools reuses it instead of trying to open a duplicate window
- if the project is closed, DevTools opens it and enables automation

After bootstrapping, connect to the matching websocket port. Low-level scripts can target a manual endpoint such as `ws://127.0.0.1:9420`; high-level entrypoints choose the project-specific port automatically.

## Hosted subpackage workflow

When the current repo is a subpackage business repo instead of a standalone Mini Program:

1. Run the resolver.
2. If multiple targets are returned, stop and ask the user which host to use.
3. After the user chooses, use that target, for example `tongcheng` or `weapp-wbfc`.
4. Start the matching watch script from `selectedTarget.devScript` so the host-mounted output stays fresh.
5. Bootstrap DevTools against `selectedTarget.devtoolsProjectPath`.
6. Use normal actions such as `reLaunch`, `tap`, `data`, and `screenshot` after the host app is open.

Example:

```bash
node "$WXA_RESOLVER" --cwd "$PWD" --target tongcheng
npm run dev:weapp-tongcheng

node "$WXA_BOOTSTRAP" \
  --project-path /abs/path/to/devtools-project

node "$WXA_RUNNER" \
  --mode connect \
  --ws-endpoint ws://127.0.0.1:9420 \
  --actions-file /tmp/wxa-actions.json
```

Important: for hosted subpackages, `--project-path` in the bootstrap step must point at the DevTools project root, not blindly at the nearest `app.json` directory. Those can differ.

In Codex-like sandboxed environments, local websocket ports may be unreachable even when DevTools is correctly configured. If `lsof` shows the target port listening but plain `node` or `curl` still cannot connect, re-run the port probe and the automator command before changing the Mini Program workflow.

There is a second sandbox failure mode worth treating separately: `cli auto` succeeds, `lsof` shows the port listening, and `curl -i http://127.0.0.1:<port>` returns `426 Upgrade Required`, but Node-based scripts still fail with messages such as "check if target project window is opened with automation enabled" or a bootstrap false negative. Treat that as a sandbox transport issue rather than a DevTools configuration issue. In that case:

1. run `cli auto --project ... --auto-port 9420`
2. verify with `lsof -nP -iTCP:9420 -sTCP:LISTEN`
3. verify with `curl -i http://127.0.0.1:9420`
4. rerun the Node automator command outside the sandbox

## Quick start

Launch DevTools for a local project and run a route smoke flow:

```bash
cat >/tmp/wxa-actions.json <<'EOF'
[
  { "type": "reLaunch", "url": "/pages/home/index" },
  { "type": "wait", "ms": 800 },
  { "type": "tap", "selector": ".primary-cta" },
  { "type": "wait", "ms": 300 },
  { "type": "data", "path": "ready" },
  { "type": "screenshot", "path": "/tmp/wxa-home.png" }
]
EOF

node "$WXA_BOOTSTRAP" \
  --project-path /abs/path/to/devtools-project

node "$WXA_RUNNER" \
  --mode connect \
  --ws-endpoint ws://127.0.0.1:9420 \
  --actions-file /tmp/wxa-actions.json
```

Connect to an existing DevTools instance:

```bash
node "$WXA_RUNNER" \
  --mode connect \
  --ws-endpoint ws://127.0.0.1:9420 \
  --actions-file /tmp/wxa-actions.json
```

If DevTools is already open but `9420` is not listening yet, turn on the DevTools port/automation setting and bootstrap the project first:

```bash
node "$WXA_BOOTSTRAP" \
  --project-path /abs/path/to/devtools-project
```

High-level single-flow entrypoint:

```bash
node "$WXA_FLOW" \
  --cwd "$PWD" \
  --target anxinchathost \
  --actions-file /tmp/wxa-actions.json
```

If you do not pass `--port` here, the flow script chooses a stable port for the current DevTools project. That prevents cross-project collisions when you switch between repos such as `anxinwechat` and `anjuke_weapp`.

Or use a built-in template:

```bash
node "$WXA_FLOW" \
  --cwd "$PWD" \
  --target anxinchathost \
  --template route-screenshot \
  --template-vars-json '{"ROUTE_URL":"/pages/home/index?id=1","ROUTE_PATH":"pages/home/index","ROUTE_QUERY":{"id":"1"},"ROUTE_TIMEOUT_MS":5000,"READY_SELECTOR":".page-root","READY_TIMEOUT_MS":5000,"SCREENSHOT_PATH":"/tmp/home.png"}'
```

Batch entrypoint:

```bash
node "$WXA_BATCH" \
  --cwd "$PWD" \
  --target anxinchathost \
  --cases-file /tmp/wxa-cases.json
```

Optional preflight before the main flow or batch:

```bash
node "$WXA_FLOW" \
  --cwd "$PWD" \
  --target anxinchathost \
  --preflight-actions-file /tmp/wxa-preflight.json \
  --actions-file /tmp/wxa-actions.json
```

```bash
node "$WXA_BATCH" \
  --cwd "$PWD" \
  --target anxinchathost \
  --preflight-actions-file /tmp/wxa-preflight.json \
  --cases-file /tmp/wxa-cases.json
```

Or use the reusable built-in preflight template:

```bash
node "$WXA_FLOW" \
  --cwd "$PWD" \
  --target anxinchathost \
  --preflight-template preflight-route-ready \
  --template route-screenshot \
  --template-vars-json '{"ROUTE_URL":"/pages/home/index?id=1","ROUTE_PATH":"pages/home/index","ROUTE_QUERY":{"id":"1"},"ROUTE_TIMEOUT_MS":5000,"READY_SELECTOR":".page-root","READY_TIMEOUT_MS":5000,"SCREENSHOT_PATH":"/tmp/home-ready.png"}'
```

```bash
node "$WXA_BATCH" \
  --cwd "$PWD" \
  --target anxinchathost \
  --preflight-template preflight-route-ready \
  --template-var ROUTE_URL='"/pages/home/index?id=1"' \
  --template-var ROUTE_PATH='"pages/home/index"' \
  --template-var ROUTE_QUERY='{"id":"1"}' \
  --template-var ROUTE_TIMEOUT_MS=5000 \
  --template-var READY_SELECTOR='".page-root"' \
  --template-var READY_TIMEOUT_MS=5000 \
  --template-var SCREENSHOT_PATH='"/tmp/home-ready.png"' \
  --cases-file /tmp/wxa-cases.json
```

Keep preflight generic and short:

1. `reLaunch` the target route
2. wait for one business selector or data condition that proves content is no longer just loading or skeleton
3. optionally capture one screenshot

If preflight fails, treat that as an environment or readiness blocker first. Do not immediately interpret a full batch of selector timeouts as twelve independent product regressions.

Or use a built-in batch template:

```bash
node "$WXA_BATCH" \
  --cwd "$PWD" \
  --target anxinchathost \
  --template batch-route-cases \
  --template-vars-json '{"ROUTE_URL":"/pages/home/index?id=1","ROUTE_PATH":"pages/home/index","ROUTE_QUERY":{"id":"1"},"ROUTE_TIMEOUT_MS":5000,"READY_SELECTOR":".page-root","READY_TIMEOUT_MS":5000,"SNAPSHOT_DATA_PATHS":["loading"],"SNAPSHOT_PATH":"/tmp/home-snapshot.json","SCREENSHOT_PATH":"/tmp/home.png"}'
```

Reusable templates:

```bash
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/route-screenshot.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/route-smoke.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/preflight-route-ready.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/route-ready-screenshot.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/page-not-skeleton.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/open-preview-then-close.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/image-preview-open-close.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/list-to-detail.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/webview-navigation.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/blank-page-diagnose.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/skeleton-stuck-diagnose.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/request-fail-diagnose.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/route-request-mock.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/storage-fixture.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/globaldata-fixture.actions.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/batch-route-cases.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/batch-smoke-cases.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/page-smoke-suite.cases.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/list-interaction-suite.cases.json
$CODEX_HOME/skills/wechat-miniprogram-automator/templates/detail-interaction-suite.cases.json
```

## Runner contract

Use `scripts/run_automator.cjs` as the default entry point. It supports a constrained action set that maps to stable `miniprogram-automator` APIs:

- route control: `reLaunch`, `navigateTo`, `redirectTo`, `switchTab`, `navigateBack`
- waiting: `wait`, `scrollTo`, `waitForRoute`, `waitForData`, `waitForSelector`, `waitForRequest`
- exploration: `inspectElements`, `findByText`, `inspectDataTree`, `findInDataTree`, `suggestSelectors`
- element actions: `tap`, `input`, `text`, `attribute`
- page state: `data`, `setData`, `callMethod`
- app hooks: `setGlobalData`, `getGlobalData`, `callAppMethod`, `callWxMethod`, `setStorage`, `getStorage`, `clearStorage`, `mockWxMethod`, `restoreWxMethod`
- artifacts: `screenshot`

The script prints one JSON object to stdout so harness code can parse the result without scraping logs.

## Guardrails

- Prefer selectors that are stable across builds. If the app exposes `data-testid`-style classes or ids, use those instead of brittle layout selectors.
- Keep action files declarative. Do not add arbitrary JS execution unless the user explicitly needs it.
- Prefer `cli auto` plus `connect` over `launch`, because opening the same DevTools project twice is unreliable and can fail with opaque automator errors.
- Re-run the flow with longer waits if the page depends on network or async hydration.
- When a selector fails, collect `data()` or a screenshot before changing the action file so the failure remains diagnosable.
- In `connect` mode, disconnect from the websocket when finished; do not close the user-owned DevTools instance. Closing DevTools from a shared session breaks subsequent routes and batch captures.
- For multi-page capture or batch smoke tests, either keep one long-lived session open or invoke the runner repeatedly in `connect` mode. Do not tear down the underlying DevTools window between pages.

## References

Open only what is needed:

- workflow details and action schema: `references/workflow.md`
- runner implementation: `scripts/run_automator.cjs`
- high-level flow entry: `scripts/run_wechat_flow.cjs`
- batch entry: `scripts/run_wechat_batch.cjs`
- reusable templates: `templates/route-screenshot.actions.json`, `templates/route-smoke.actions.json`, `templates/batch-route-cases.json`, `templates/batch-smoke-cases.json`
- readiness templates: `templates/preflight-route-ready.actions.json`, `templates/route-ready-screenshot.actions.json`, `templates/page-not-skeleton.actions.json`
- preview templates: `templates/open-preview-then-close.actions.json`, `templates/image-preview-open-close.actions.json`
- navigation templates: `templates/list-to-detail.actions.json`, `templates/webview-navigation.actions.json`
- diagnose templates: `templates/blank-page-diagnose.actions.json`, `templates/skeleton-stuck-diagnose.actions.json`, `templates/request-fail-diagnose.actions.json`
- request-mock template: `templates/route-request-mock.actions.json`
- batch suites: `templates/page-smoke-suite.cases.json`, `templates/list-interaction-suite.cases.json`, `templates/detail-interaction-suite.cases.json`
- fixture templates: `templates/storage-fixture.actions.json`, `templates/globaldata-fixture.actions.json`
- project-shape resolver: `scripts/resolve_wechat_project.cjs`
- DevTools bootstrap helper: `scripts/ensure_devtools_session.cjs`
