# Workflow Reference

## Modes

## Resolve project first

Before choosing a mode, resolve whether the current repo is:

- a standalone Mini Program root
- a hosted subpackage repo that compiles into a separate host Mini Program

Use:

```bash
node "$WXA_RESOLVER" --cwd "$PWD"
```

If the resolver returns `hosted-subpackage`, bootstrap DevTools with `selectedTarget.devtoolsProjectPath`, not the current repo path.

Some repos have two different roots:

- runtime Mini Program root: contains `app.json`
- DevTools project root: contains `project.config.json`

Do not assume they are the same directory.

If the resolver returns multiple hosted targets, stop and ask the user which host to use before bootstrapping DevTools or running actions. Do not silently default to the first target unless it is the only target.

## Bootstrap before connect

Prefer this sequence:

1. `node "$WXA_BOOTSTRAP" --project-path /abs/path/to/devtools-project`
2. `node "$WXA_RUNNER" --mode connect --ws-endpoint ws://127.0.0.1:9420 ...`

Why: opening the same DevTools project twice is unreliable. `cli auto` is a better canonical entrypoint because it can reuse an already-open project while still enabling the automation port.

For the higher-level `run_wechat_flow.cjs` and `run_wechat_batch.cjs` entrypoints, `--port` is optional. If omitted, they derive a stable port from `devtoolsProjectPath` so different Mini Program projects do not accidentally share the same websocket session.

### Launch mode

Use launch mode only as a fallback when you need a clean temporary session and you know the target project is not already open in DevTools.

Required fields:

- `--mode launch`
- `--project-path /abs/path/to/project`

For hosted subpackages, `/abs/path/to/project` means the DevTools project root, not blindly the nearest `app.json` directory.

Optional fields:

- `--cli-path /Applications/wechatwebdevtools.app/Contents/MacOS/cli`
- `--port 9420`
- `--account <wechat account>`
- `--ticket <ticket>`
- `--cwd <working directory>`
- `--trust-project`

The underlying package defaults to the macOS CLI path above and uses port `9420` unless another open port is chosen.

### Connect mode

Use connect mode when DevTools is already open for the target project.

Required fields:

- `--mode connect`
- `--ws-endpoint ws://127.0.0.1:9420`

This is the safer choice for debugging an already-running or automation-bootstrapped session.

Before using connect mode in real workflows:

1. Turn on the DevTools service-port or automation setting in the GUI.
2. If the project was not opened through automation yet, run:

```bash
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto \
  --project /abs/path/to/miniprogram \
  --auto-port 9420
```

3. Verify the port is listening:

```bash
lsof -nP -iTCP:9420 -sTCP:LISTEN
```

If `9420` is listening, a direct HTTP probe usually returns `426 Upgrade Required`, which is a good sign that the websocket endpoint is alive:

```bash
curl -i http://127.0.0.1:9420
```

## Action file shape

The runner accepts either `--actions-file path/to/file.json` or `--actions-json '[...]'`.

Each action is an object with a required `type`.

Supported actions:

- `{"type":"reLaunch","url":"/pages/home/index"}`
- `{"type":"navigateTo","url":"/pages/detail/index?id=1"}`
- `{"type":"redirectTo","url":"/pages/login/index"}`
- `{"type":"switchTab","url":"/pages/tabbar/mine/index"}`
- `{"type":"navigateBack"}`
- `{"type":"wait","ms":500}`
- `{"type":"wait","condition":"return !!window.__HYDRATED__"}`
- `{"type":"scrollTo","top":1200,"waitMs":300}`
- `{"type":"waitForRoute","path":"page/anxinwechatZF/pages/zufangList/index","query":{"activityId":"zf2026032384310"},"timeoutMs":5000,"pollMs":200}`
- `{"type":"waitForData","path":"ready","truthy":true,"timeoutMs":5000,"pollMs":200}`
- `{"type":"waitForData","path":"form","equals":{"submitted":true},"timeoutMs":5000,"pollMs":200}`
- `{"type":"waitForSelector","selector":".house-list","timeoutMs":5000,"pollMs":200}`
- `{"type":"waitForSelector","scopeSelector":".broker-card","scopeSelectorIndex":0,"selector":".primary-btn","timeoutMs":5000,"pollMs":200}`
- `{"type":"waitForSelector","selector":".certificate-icon","selectorAttributeName":"class","selectorAttributeValue":"is-active","selectorAttributeExact":false,"timeoutMs":5000,"pollMs":200}`
- `{"type":"waitForRequest","urlIncludes":"detail","ok":true,"statusCode":200,"timeoutMs":5000,"pollMs":200}`
- `{"type":"snapshot","dataPaths":["list","loading"],"path":"/tmp/page-snapshot.json","timeoutMs":3000}`
- For Taro React pages, `snapshot.dataPaths` often works better with `root` than with hook-state names such as `loading` or `houseData`.
- `{"type":"inspectElements","selector":".house-list","limit":5,"attributes":["class","id"],"includeSize":true}`
- `{"type":"findByText","selector":"view","text":"skeleton","limit":5,"searchAttributes":["class","id"]}`
- `{"type":"inspectDataTree","path":"root","limit":20}`
- `{"type":"findInDataTree","path":"root","text":"skeleton","limit":10}`
- `{"type":"suggestSelectors","path":"root","limit":10,"minCount":1}`
- `{"type":"tap","selector":".submit-btn"}`
- `{"type":"tap","scopeSelector":".broker-card","scopeSelectorIndex":0,"selector":".primary-btn"}`
- `{"type":"tap","selector":".tab-item","selectorText":"详情","selectorTextExact":false}`
- `{"type":"tap","selector":".certificate-icon","selectorIndex":1}`
- `{"type":"tap","xpath":"//view[@id='submit']"}`
- `{"type":"input","selector":"input[name='phone']","value":"13800138000"}`
- `{"type":"text","selector":".status-text"}`
- `{"type":"attribute","selector":".status-text","name":"class"}`
- `{"type":"data","path":"form.phone"}`
- `{"type":"setData","data":{"loaded":true}}`
- `{"type":"callMethod","method":"onPullDownRefresh","args":[]}`
- `{"type":"setGlobalData","path":"harness.flag","value":{"enabled":true}}`
- `{"type":"setGlobalData","data":{"cityId":"1","channel":"codex"}}`
- `{"type":"getGlobalData","path":"harness.flag"}`
- `{"type":"callAppMethod","method":"AJKMPS.getCityInfo","args":[]}`
- `{"type":"callWxMethod","method":"getSystemInfoSync","args":[]}`
- `{"type":"setStorage","key":"token","value":"abc123"}`
- `{"type":"getStorage","key":"token"}`
- `{"type":"clearStorage"}`
- `{"type":"mockWxMethod","method":"request","result":{"statusCode":200,"data":{"ok":true}},"args":[]}`
- `{"type":"restoreWxMethod","method":"request"}`
- `{"type":"screenshot","path":"/tmp/miniprogram.png"}`

## Output contract

The runner writes one JSON object to stdout:

```json
{
  "ok": true,
  "mode": "connect",
  "consoleEventCount": 0,
  "consoleTail": [],
  "exceptionCount": 0,
  "exceptionTail": [],
  "requestEventCount": 1,
  "requestTail": [
    {
      "method": "GET",
      "url": "https://example.test/api/detail?id=1",
      "startAt": "2026-03-26T10:00:00.000Z",
      "endAt": "2026-03-26T10:00:00.120Z",
      "durationMs": 120,
      "statusCode": 200,
      "ok": true,
      "error": null
    }
  ],
  "results": [
    {
      "index": 0,
      "type": "reLaunch",
      "value": {
        "path": "/pages/home/index",
        "query": {}
      }
    }
  ]
}
```

When `--artifacts-dir` is provided, the runner also writes `trace.json` under that directory and stores failure screenshots and snapshots under `diagnostics/`.

For `snapshot` actions:

- each requested `dataPath` is resolved with `page.data(path)`
- `undefined` values are tracked via `dataMeta[path].found = false`
- if every requested path is missing but `page.data().root` exists, the runner includes a compact `dataTree` summary automatically
- this is common on Taro React pages where rendered structure is present under `root` but hook state is not exposed as a plain page-data key

For request telemetry:

- the runner instruments `wx.request` automatically for the current session
- each completed request is summarized as:
  - `method`
  - `url`
  - `startAt`
  - `endAt`
  - `durationMs`
  - `statusCode`
  - `ok`
  - `error`
- runner output includes `requestEventCount`
- runner output includes `requestTail` with the most recent completed requests
- use `waitForRequest` when a page should only be considered ready after one key request succeeds

## Request mock guidance

Prefer request mock only when:

- the upstream API is unstable
- you need a repeatable regression harness for a UI state
- you want to prove a code fix independent of external environment noise

Recommended `mockWxMethod("request")` shape:

- match one narrow URL token instead of mocking every request blindly
- always call `success` and `complete` for matched requests
- call `fail` and `complete` for unmatched requests when you want the page to surface accidental overreach quickly
- return a minimal request-task object with `abort`, `onHeadersReceived`, and `offHeadersReceived`
- always add a trailing `restoreWxMethod` action so the mock does not leak into later cases

Recommended mock response structure:

- `statusCode`
- `data`
- `header`
- `cookies`

Built-in template:

- `route-request-mock`

Template variables:

- `ROUTE_URL`
- `ROUTE_PATH`
- `ROUTE_QUERY`
- `ROUTE_TIMEOUT_MS`
- `REQUEST_URL_INCLUDES`
- `REQUEST_TIMEOUT_MS`
- `RESPONSE_STATUS_CODE`
- `RESPONSE_DATA`
- `RESPONSE_HEADER`
- `READY_SELECTOR`
- `READY_TIMEOUT_MS`
- `SCREENSHOT_PATH`

Example:

```bash
node "$WXA_FLOW" \
  --cwd "$PWD" \
  --target anxinchathost \
  --template route-request-mock \
  --template-vars-json '{"ROUTE_URL":"/pages/home/index?id=1","ROUTE_PATH":"pages/home/index","ROUTE_QUERY":{"id":"1"},"ROUTE_TIMEOUT_MS":5000,"REQUEST_URL_INCLUDES":"api/detail","REQUEST_TIMEOUT_MS":5000,"RESPONSE_STATUS_CODE":200,"RESPONSE_DATA":{"ok":true,"title":"mocked"},"RESPONSE_HEADER":{"content-type":"application/json"},"READY_SELECTOR":".page-root","READY_TIMEOUT_MS":5000,"SCREENSHOT_PATH":"/tmp/home-mocked.png"}'
```

## Record / replay draft

This is still a design draft, not a finished runner feature.

Recommended direction:

1. record only the request summary first, not full bodies by default
2. store fixtures as JSON arrays under a dedicated artifact path such as `artifacts/requests.json`
3. keep one fixture entry per completed request with:
   - `method`
   - `url`
   - `statusCode`
   - `ok`
   - `durationMs`
   - optional `responseData` when the user explicitly opts in
4. replay should prefer URL token matching plus method matching, not full URL string matching only
5. replay should fail closed when no fixture matches, so false positives are obvious
6. replay should compose with route templates and readiness selectors instead of replacing them

Suggested phases:

1. `recordRequestTail`: save recent summarized requests to a fixture file
2. `mockFromFixture`: replay one or more fixture entries through `mockWxMethod("request")`
3. optional body capture behind an explicit flag for privacy and artifact size control

This keeps the first replay version generic and low-risk: enough for reproducible UI harnesses without turning the skill into a heavy network recorder.

On failures it writes:

```json
{
  "ok": false,
  "error": "Selector not found: .submit-btn",
  "consoleEventCount": 0,
  "consoleTail": [],
  "exceptionCount": 0,
  "exceptionTail": [],
  "requestEventCount": 2,
  "requestTail": [
    {
      "method": "GET",
      "url": "https://example.test/api/list",
      "startAt": "2026-03-26T10:00:00.000Z",
      "endAt": "2026-03-26T10:00:00.080Z",
      "durationMs": 80,
      "statusCode": null,
      "ok": false,
      "error": "request:fail"
    }
  ],
  "diagnostics": {
    "snapshotPath": "/tmp/wechat-automator-failure-123.json",
    "screenshotPath": "/tmp/wechat-automator-failure-123.png"
  },
  "failedAction": {
    "type": "tap",
    "selector": ".submit-btn"
  }
}
```

High-level `run_wechat_flow.cjs` and `run_wechat_batch.cjs` reports may also include a `fallback` object on `bootstrap` or `probe` failure:

```json
{
  "ok": false,
  "phase": "probe",
  "error": "Websocket probe failed",
  "fallback": {
    "suspectedSandboxFalseNegative": true,
    "lsofListening": true,
    "curlUpgradeRequired": true,
    "curlStatusLine": "HTTP/1.1 426 Upgrade Required",
    "manualSteps": [
      "/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto --project /abs/path/to/project --auto-port 9420",
      "lsof -nP -iTCP:9420 -sTCP:LISTEN",
      "curl -i http://127.0.0.1:9420",
      "node /path/to/run_automator.cjs --mode connect --ws-endpoint ws://127.0.0.1:9420 --actions-file /tmp/wxa-actions.json"
    ],
    "explanation": "The DevTools port appears alive from shell probes, so this failure is likely a sandbox false negative in Node-based bootstrap/probe logic."
  }
}
```

Read `fallback` as an execution hint, not a guaranteed diagnosis. When `suspectedSandboxFalseNegative` is `true`, prefer following `manualSteps` before changing project paths, selectors, or Mini Program code.

High-level `run_wechat_flow.cjs` and `run_wechat_batch.cjs` may also include a `preflight` section when you pass `--preflight-actions-file`, `--preflight-actions-json`, or `--preflight-template`.
If preflight fails, the top-level report stops early with:

```json
{
  "ok": false,
  "phase": "preflight",
  "environmentBlocked": true,
  "error": "Preflight failed before the batch started. Treat this as an environment or readiness blocker until proven otherwise."
}
```

Use this to separate:

- environment or data-source failures such as skeleton-only renders, loading loops, or repeated `request:fail`
- real business regressions on the clickable elements you actually want to validate

## Failure taxonomy

High-level reports now expose `failureType`.

Current values:

- `environment_blocked`
- `bootstrap_failed`
- `probe_failed`
- `route_failed`
- `request_failed`
- `selector_failed`
- `assertion_failed`

Recommended meaning:

- `environment_blocked`: preflight failed before the real flow or batch started
- `bootstrap_failed`: DevTools bootstrap did not produce a usable automation session
- `probe_failed`: websocket probe failed after bootstrap
- `route_failed`: route transition or route readiness did not complete
- `request_failed`: request assertion failed, or readiness checks failed with recent request failures present
- `selector_failed`: selector lookup or interaction failed without stronger request evidence
- `assertion_failed`: fallback bucket for failures that are not clearly route, request, or selector issues

Batch reports also expose `summary.failureTypes` so one run can be summarized by failure class instead of only raw pass/fail counts.

Top-level reports also expose `artifactIndex`.

Typical fields:

- flow:
  - `successScreenshots`
  - `successSnapshots`
  - `failureScreenshot`
  - `failureSnapshot`
  - `runnerTracePath`
  - `reportPath`
- batch:
  - `successScreenshots`
  - `failureScreenshots`
  - `failureSnapshots`
  - `tracePaths`
  - `reportPaths`

This keeps evidence lookup at the top level instead of forcing the user or agent to walk every case directory by hand.

The built-in `preflight-route-ready` template is the default generic starting point when you only need to prove one route has left loading or skeleton state.

## Recommended harness patterns

The top-level single-flow `report.json` is also summary-first. It keeps compact `resolve`, `target`, `bootstrap`, and `probe` metadata plus the full `run` payload.
`run_wechat_flow.cjs` accepts `--template <name>` for built-in action templates under `templates/`.
Pass `--template-vars-json` or repeated `--template-var KEY=value` when the template contains placeholders such as `{{ROUTE_URL}}`, `{{ROUTE_PATH}}`, `{{ROUTE_QUERY}}`, `{{READY_SELECTOR}}`, or output paths.
Use `run_wechat_flow.cjs --list-templates` to discover built-in single-flow templates.
Both high-level entrypoints now serialize access to the same DevTools session with a lock keyed by `devtoolsProjectPath + port`. Inspect `session.lockWaitedMs` when you need to explain why one run waited for another.
If a previous owner process has already died, the stale lock is reclaimed automatically from `owner.json`.

Useful single-flow templates:

- `preflight-route-ready`
- `route-ready-screenshot`
- `list-to-detail`
- `page-not-skeleton`
- `open-preview-then-close`
- `image-preview-open-close`
- `webview-navigation`
- `blank-page-diagnose`
- `skeleton-stuck-diagnose`
- `request-fail-diagnose`
- `route-request-mock`

### Route smoke check

1. `reLaunch` the target page.
2. Prefer `waitForRoute` over a blind fixed wait.
3. Prefer `waitForSelector` or `waitForData` for business readiness.
4. Optionally save a `snapshot` before the final artifact.
5. Capture a `screenshot`.
6. On failures, prefer the runner-generated `diagnostics.snapshotPath` over guessing page state from logs.
7. On Taro React pages, if `snapshot.data` looks empty, inspect `dataMeta` first before assuming the page has no state.

### Canary before a long run

Before a long flow or multi-case batch:

1. Start with a short canary or preflight action list.
2. Keep it to one route and one business readiness check.
3. Do not assert deep interaction details yet.
4. Only run the full batch after the canary proves the page has moved beyond loading or skeleton state.

Good preflight examples:

- list page: wait for the first real card, not just the list container
- detail page: wait for a content selector such as a swiper image, map block, or bottom bar, not just the page route
- forms: wait for the first editable field or submit button, not just the shell layout

This pattern stays generic across projects because it validates readiness, not project-specific content.

### Skeleton and loading diagnostics

Do not treat the page root as equivalent to readiness.

- `container selector` examples: page root, list shell, tab container, static header, empty card wrapper
- `business selector` examples: first real card, populated title block, loaded swiper image, enabled CTA, rendered map block
- If only the container selector appears, the page may still be stuck in skeleton or loading state
- If the route matches but the business selector never appears, prefer diagnosing environment, data source, or request failures before blaming every downstream click target

Practical order:

1. `waitForRoute`
2. `waitForSelector` on one business selector
3. only then run deeper taps, snapshots, or assertions

When the page still does not become ready:

1. inspect `requestTail` for repeated `ok: false` requests
2. inspect whether the last matched request returned an unexpected `statusCode`
3. only then decide whether to rewrite selectors or patch business code

When debugging a stall:

1. use `snapshot` with `dataPaths: ["root"]`
2. run `findInDataTree` for text such as `loading`, `skeleton`, or placeholder copy
3. inspect `consoleTail`, `exceptionTail`, and any request failures before rewriting selectors

### Scoped selector guidance

Use scoped selector parameters when the page has repeated blocks with the same child button or icon.

- `scopeSelector`: parent block selector
- `scopeSelectorIndex`: which matched parent block to use
- `selector`: child selector inside that scoped block

Example:

```json
{
  "type": "tap",
  "scopeSelector": ".broker-card",
  "scopeSelectorIndex": 0,
  "selector": ".primary-btn"
}
```

Current limitation:

- scoped XPath lookup is not supported
- when you need scope, prefer `scopeSelector + selector`

### Text and attribute targeting

When `selector` alone matches too many elements, you can refine the match with:

- `selectorText`
- `selectorTextExact`
- `selectorAttributeName`
- `selectorAttributeValue`
- `selectorAttributeExact`

Examples:

```json
{
  "type": "tap",
  "selector": ".tab-item",
  "selectorText": "详情",
  "selectorTextExact": false
}
```

```json
{
  "type": "tap",
  "selector": ".certificate-icon",
  "selectorAttributeName": "class",
  "selectorAttributeValue": "is-active",
  "selectorAttributeExact": false
}
```

Matching order:

1. scope filtering
2. selector match
3. text and attribute filtering
4. `selectorIndex` if still needed

### Reusable preflight template

Use `preflight-route-ready` when you want one generic canary that works for most page-level checks:

- `ROUTE_URL`: full route passed to `reLaunch`
- `ROUTE_PATH`: expected route path for `waitForRoute`
- `ROUTE_QUERY`: expected query object for `waitForRoute`
- `ROUTE_TIMEOUT_MS`: route wait timeout
- `READY_SELECTOR`: one business selector that proves the page is really ready
- `READY_TIMEOUT_MS`: readiness wait timeout
- `SCREENSHOT_PATH`: screenshot written after the page is ready

Flow example:

```bash
node "$WXA_FLOW" \
  --cwd "$PWD" \
  --target anxinchathost \
  --preflight-template preflight-route-ready \
  --template route-screenshot \
  --template-vars-json '{"ROUTE_URL":"/pages/home/index?id=1","ROUTE_PATH":"pages/home/index","ROUTE_QUERY":{"id":"1"},"ROUTE_TIMEOUT_MS":5000,"READY_SELECTOR":".page-root","READY_TIMEOUT_MS":5000,"SCREENSHOT_PATH":"/tmp/home-ready.png"}'
```

Batch example:

```bash
node "$WXA_BATCH" \
  --cwd "$PWD" \
  --target anxinchathost \
  --preflight-template preflight-route-ready \
  --template-vars-json '{"ROUTE_URL":"/pages/home/index?id=1","ROUTE_PATH":"pages/home/index","ROUTE_QUERY":{"id":"1"},"ROUTE_TIMEOUT_MS":5000,"READY_SELECTOR":".page-root","READY_TIMEOUT_MS":5000,"SCREENSHOT_PATH":"/tmp/home-ready.png"}' \
  --cases-file /tmp/wxa-cases.json
```

Do not use the page root alone as `READY_SELECTOR` if the framework renders a shell immediately. Prefer the first real business selector that disappears only after loading is complete.

### Combination templates

`route-ready-screenshot`

- use when you only need route confirmation, one readiness selector, and one screenshot

`page-not-skeleton`

- use when you want one root snapshot plus one skeleton text probe before waiting for a business selector
- recommended variables:
  - `SKELETON_TEXT`
  - `SKELETON_LIMIT`

`open-preview-then-close`

- use when a page opens a preview layer and exposes stable open and close selectors
- recommended variables:
  - `OPEN_SELECTOR`
  - `OPEN_SELECTOR_INDEX`
  - `OPEN_TIMEOUT_MS`
  - `PREVIEW_WAIT_MS`
  - `OPEN_SCREENSHOT_PATH`
  - `CLOSE_SELECTOR`
  - `CLOSE_SELECTOR_INDEX`
  - `CLOSE_TIMEOUT_MS`
  - `CLOSE_WAIT_MS`
  - `CLOSE_SCREENSHOT_PATH`

`image-preview-open-close`

- same structure as `open-preview-then-close`, but named for image preview flows so discovery is easier

`list-to-detail`

- use when the main risk is the transition from a list card into a detail page
- recommended variables:
  - `LIST_ROUTE_URL`
  - `LIST_ROUTE_PATH`
  - `LIST_ROUTE_QUERY`
  - `LIST_ROUTE_TIMEOUT_MS`
  - `LIST_READY_SELECTOR`
  - `LIST_READY_TIMEOUT_MS`
  - `LIST_ITEM_SELECTOR`
  - `LIST_ITEM_SELECTOR_INDEX`
  - `DETAIL_ROUTE_PATH`
  - `DETAIL_ROUTE_QUERY`
  - `DETAIL_ROUTE_TIMEOUT_MS`
  - `DETAIL_READY_SELECTOR`
  - `DETAIL_READY_TIMEOUT_MS`
  - `SCREENSHOT_PATH`

`webview-navigation`

- use when a click should open an in-app webview page
- recommended variables:
  - `TRIGGER_SELECTOR`
  - `TRIGGER_SELECTOR_INDEX`
  - `TRIGGER_TIMEOUT_MS`
  - `WEBVIEW_ROUTE_PATH`
  - `WEBVIEW_ROUTE_QUERY`
  - `WEBVIEW_ROUTE_TIMEOUT_MS`
  - `WEBVIEW_READY_SELECTOR`
  - `WEBVIEW_READY_TIMEOUT_MS`
  - `SCREENSHOT_PATH`

### Batch page screenshots

Use `run_wechat_batch.cjs` when you want one batch report with per-case subreports.
`run_wechat_batch.cjs` accepts `--template <name>` for built-in batch cases under `templates/`.
Batch templates use the same placeholder mechanism as single-flow templates.
Use `run_wechat_batch.cjs --list-templates` to discover built-in batch templates.
Its output is grouped into `[batch]` and `[action]` so reusable canary and request-mock templates stay discoverable from the same entrypoint.

Useful batch templates:

- `page-smoke-suite`
- `list-interaction-suite`
- `detail-interaction-suite`

The top-level batch `report.json` is intentionally summary-first. It keeps compact `resolve`, `target`, `bootstrap`, and `probe` metadata plus per-case summaries. Use each case `reportPath` when you need the full runner payload or diagnostics.

Example `cases.json`:

```json
{
  "defaults": {
    "beforeEach": [
      { "type": "reLaunch", "url": "/page/anxinwechatZF/pages/zufangList/index?activityId=zf2026032384310" }
    ]
  },
  "cases": [
    {
      "name": "zufang-list-snapshot",
      "actions": [
        { "type": "waitForRoute", "path": "page/anxinwechatZF/pages/zufangList/index", "query": { "activityId": "zf2026032384310" }, "timeoutMs": 5000 },
        { "type": "snapshot", "dataPaths": ["list", "loading"], "path": "/tmp/zufang-list-snapshot.json" }
      ]
    },
    {
      "name": "zufang-list-screenshot",
      "actions": [
        { "type": "waitForSelector", "selector": ".house-list", "timeoutMs": 5000 },
        { "type": "screenshot", "path": "/tmp/zufang-list.png" }
      ]
    }
  ]
}
```

Run:

```bash
node "$CODEX_HOME/skills/wechat-miniprogram-automator/scripts/run_wechat_batch.cjs" \
  --cwd "$PWD" \
  --target anxinchathost \
  --cases-file /tmp/wxa-cases.json
```

The top-level batch `report.json` keeps only a per-case summary plus each case `reportPath`. Open the child report when you need the full runner payload.
For faster batches, the batch runner defaults to a lightweight websocket probe that skips `currentPage()`.
If the batch file provides `defaults.beforeEach` or `defaults.afterEach`, those actions are prepended or appended to every case automatically.

Use one automation-backed DevTools session, then iterate through routes with repeated `connect` calls or a single long-lived client.

Recommended loop:

1. Start DevTools once with `cli auto --project ... --auto-port 9420`.
2. For each page, run `reLaunch`, `wait`, and `screenshot`.
3. Save a `report.json` beside the images.

Important: in `connect` mode, disconnect only from the websocket. Do not call `close()` on the Mini Program object after each page or the DevTools automation session will disappear after the first success.

### Form submission

1. `reLaunch` or `navigateTo` the form page.
2. `input` into each field.
3. `tap` the submit selector.
4. Assert with `text`, `attribute`, or `data`.

### API mocking

1. `mockWxMethod` before entering the flow.
2. Run the route and UI actions.
3. `restoreWxMethod` before closeout.

### Storage fixtures

1. Use `clearStorage` at the start of the case if previous runs may have left state behind.
2. Use `setStorage` to inject login flags, guide dismissal markers, or cached business context.
3. Use `getStorage` when you need to assert that the page or app updated storage as expected.

### App fixtures

1. Use `setGlobalData` when the host Mini Program expects data under `getApp().globalData`.
2. Use `getGlobalData` to verify that the app-level fixture is present before the route under test runs.
3. Use `callAppMethod` with dotted paths such as `AJKMPS.getCityInfo` for host-provided helpers or adapter objects.

### Page exploration

1. Use `inspectElements` when you already know a broad selector and need a compact summary of matching nodes.
2. Use `findByText` when you know visible text, class fragments, or ids but not the final selector yet.
3. Keep exploration bounded with `limit`; otherwise large list pages can return too much noise.
4. If the element API cannot see a node clearly, fall back to `inspectDataTree` or `findInDataTree` against `page.data()`.
5. Use `suggestSelectors` when you want class-based selector candidates that are validated against the live page.
6. For Taro pages, `inspectDataTree path=root` is often more useful than `data path=loading` or `data path=houseData`.

## Troubleshooting

- `Wechat web devTools not found`: pass `--cli-path` explicitly.
- `Project path ... doesn't exist`: resolve the app path before calling launch mode.
- `Failed connecting ... automation enabled`: first check whether `9420` is listening. If not, enable DevTools automation and run `cli auto --project ... --auto-port 9420`. If `9420` is listening but the command still fails only inside the agent sandbox, retry with elevated execution because the sandbox may block local websocket access.
- `Bootstrap failed` or `portListeningBefore: false` even though `cli auto` already succeeded: if `lsof -nP -iTCP:<port> -sTCP:LISTEN` shows the port and `curl -i http://127.0.0.1:<port>` returns `426 Upgrade Required`, treat it as a sandbox false negative in Node-based probe/bootstrap logic. Prefer explicit `cli auto` first, then rerun the Node automator command outside the sandbox.
- Empty screenshot path: create the parent directory first; the runner does not create nested directories.
- First page succeeds but every later page fails to connect: the session was probably closed after page 1. Use `disconnect()` for `connect` mode and reserve `close()` for `launch` mode.
- Existing user-opened DevTools window should usually stay open after the task. When connected to a user-owned session, detach cleanly instead of closing the app.
