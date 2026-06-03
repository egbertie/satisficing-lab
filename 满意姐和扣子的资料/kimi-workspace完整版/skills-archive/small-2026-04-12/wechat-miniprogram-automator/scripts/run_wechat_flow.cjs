#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function printHelp() {
  const lines = [
    'Usage:',
    '  node run_wechat_flow.cjs --cwd /abs/workspace --target anxinchathost --actions-file /tmp/actions.json',
    '',
    'Options:',
    '  --cwd <dir>            Workspace to resolve. Defaults to process.cwd().',
    '  --target <name>        Explicit hosted target when multiple candidates exist.',
    '  --actions-file <path>  JSON file containing runner actions.',
    '  --actions-json <json>  Inline JSON array of runner actions.',
    '  --template <name>      Built-in action template name or path under templates/.',
    '  --template-var <k=v>   Template variable. Repeatable.',
    '  --template-vars-json <json> JSON object of template variables.',
    '  --preflight-actions-file <path> Optional canary actions run before the main flow.',
    '  --preflight-actions-json <json> Optional inline canary actions run before the main flow.',
    '  --preflight-template <name> Optional canary template name or path under templates/.',
    '  --list-templates       Print available built-in action templates and exit.',
    '  --artifacts-dir <dir>  Directory for report output. Defaults to output/wechat-miniprogram-automator or /tmp/wechat-miniprogram-automator.',
    '  --port <number>        Automation websocket port. Defaults to a stable per-project port.',
    '  --timeout-ms <ms>      Bootstrap/probe timeout. Defaults to 5000.',
    '  --probe-timeout-ms <ms> Probe timeout override. Defaults to --timeout-ms.',
    '  --lock-timeout-ms <ms> Max wait for the DevTools session lock. Defaults to 180000.',
    '  --skip-current-page-probe Skip currentPage() during websocket probe.',
    '  --retries <n>          Bootstrap retries. Defaults to 2.',
    '  --json                 Print compact JSON only.',
    '  --help                 Show this help.',
  ];

  process.stdout.write(`${lines.join('\n')}\n`);
}

function parseArgs(argv) {
  const args = {
    cwd: process.cwd(),
    artifacts_dir: null,
    port: null,
    timeout_ms: '5000',
    probe_timeout_ms: null,
    lock_timeout_ms: '180000',
    retries: '2',
    skip_current_page_probe: false,
    template_var: [],
    json: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];

    if (token === '--help') {
      args.help = true;
      continue;
    }

    if (token === '--json') {
      args.json = true;
      continue;
    }

    if (token === '--list-templates') {
      args.list_templates = true;
      continue;
    }

    if (token === '--template-var') {
      const value = argv[index + 1];
      if (value == null || value.startsWith('--')) {
        throw new Error('Missing value for --template-var');
      }
      args.template_var.push(value);
      index += 1;
      continue;
    }

    if (token === '--skip-current-page-probe') {
      args.skip_current_page_probe = true;
      continue;
    }

    if (!token.startsWith('--')) {
      throw new Error(`Unexpected argument: ${token}`);
    }

    const key = token.slice(2).replace(/-/g, '_');
    const value = argv[index + 1];
    if (value == null || value.startsWith('--')) {
      throw new Error(`Missing value for ${token}`);
    }
    args[key] = value;
    index += 1;
  }

  args.cwd = path.resolve(args.cwd);
  args.artifacts_dir = args.artifacts_dir ? path.resolve(args.artifacts_dir) : null;
  args.port = args.port == null ? null : Number(args.port);
  args.timeout_ms = Number(args.timeout_ms);
  args.probe_timeout_ms = args.probe_timeout_ms == null ? args.timeout_ms : Number(args.probe_timeout_ms);
  args.lock_timeout_ms = Number(args.lock_timeout_ms);
  args.retries = Number(args.retries);
  if (args.port != null && (!Number.isFinite(args.port) || args.port <= 0)) {
    throw new Error('--port must be a positive number');
  }
  if (!Number.isFinite(args.timeout_ms) || args.timeout_ms <= 0) {
    throw new Error('--timeout-ms must be a positive number');
  }
  if (!Number.isFinite(args.probe_timeout_ms) || args.probe_timeout_ms <= 0) {
    throw new Error('--probe-timeout-ms must be a positive number');
  }
  if (!Number.isFinite(args.lock_timeout_ms) || args.lock_timeout_ms <= 0) {
    throw new Error('--lock-timeout-ms must be a positive number');
  }
  if (!Number.isInteger(args.retries) || args.retries <= 0) {
    throw new Error('--retries must be a positive integer');
  }

  return args;
}

function defaultArtifactsDir(cwd) {
  const outputDir = path.join(cwd, 'output');
  if (fs.existsSync(outputDir) && fs.statSync(outputDir).isDirectory()) {
    return path.join(outputDir, 'wechat-miniprogram-automator');
  }
  return path.join('/tmp', 'wechat-miniprogram-automator');
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
  return dirPath;
}

function buildArtifacts(args) {
  const rootDir = ensureDir(args.artifacts_dir || defaultArtifactsDir(args.cwd));
  const runId = new Date().toISOString().replace(/[:.]/g, '-');
  const runDir = ensureDir(path.join(rootDir, runId));
  return {
    rootDir,
    runDir,
    reportPath: path.join(runDir, 'report.json'),
  };
}

function writeReport(reportPath, payload) {
  fs.writeFileSync(reportPath, JSON.stringify(payload, null, 2));
}

function runJsonScript(scriptPath, scriptArgs, options = {}) {
  const finalArgs = options.supportsJsonFlag ? [...scriptArgs, '--json'] : scriptArgs;
  const result = spawnSync('node', [scriptPath, ...finalArgs], {
    encoding: 'utf8',
  });

  let parsed = null;
  const stdout = result.stdout || '';
  try {
    parsed = stdout ? JSON.parse(stdout) : null;
  } catch (error) {
    parsed = null;
  }

  return {
    exitCode: result.status,
    stdout,
    stderr: result.stderr || '',
    parsed,
  };
}

function runTextCommand(command, commandArgs) {
  const result = spawnSync(command, commandArgs, {
    encoding: 'utf8',
  });

  return {
    exitCode: result.status,
    stdout: result.stdout || '',
    stderr: result.stderr || '',
  };
}

function collectPortFallback(projectPath, port, wsEndpoint) {
  const lsofResult = runTextCommand('lsof', [
    '-nP',
    `-iTCP:${port}`,
    '-sTCP:LISTEN',
  ]);
  const curlResult = runTextCommand('curl', [
    '-i',
    `http://127.0.0.1:${port}`,
  ]);

  const lsofListening = lsofResult.exitCode === 0;
  const curlStatusLine = (curlResult.stdout || '')
    .split('\n')
    .map((line) => line.trim())
    .find((line) => line.startsWith('HTTP/'));
  const curlUpgradeRequired = typeof curlStatusLine === 'string' && curlStatusLine.includes('426');
  const suspectedSandboxFalseNegative = lsofListening && curlUpgradeRequired;

  return {
    suspectedSandboxFalseNegative,
    lsofListening,
    curlUpgradeRequired,
    curlStatusLine: curlStatusLine || null,
    manualSteps: [
      `/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto --project ${projectPath} --auto-port ${port}`,
      `lsof -nP -iTCP:${port} -sTCP:LISTEN`,
      `curl -i http://127.0.0.1:${port}`,
      `node ${path.join(__dirname, 'run_automator.cjs')} --mode connect --ws-endpoint ${wsEndpoint} --actions-file /tmp/wxa-actions.json`,
    ],
    explanation: suspectedSandboxFalseNegative
      ? 'The DevTools port appears alive from shell probes, so this flow failure is likely a sandbox false negative in Node-based bootstrap/probe logic. Prefer explicit cli auto plus rerunning the Node automator command outside the sandbox.'
      : 'The DevTools port does not look healthy enough for the known sandbox false-negative pattern. Check DevTools automation settings and project selection first.',
    lsof: lsofResult,
    curl: {
      exitCode: curlResult.exitCode,
      statusLine: curlStatusLine || null,
      stderr: curlResult.stderr,
    },
  };
}

function normalizeSelection(resolveOutput, explicitTarget) {
  if (!resolveOutput || resolveOutput.kind !== 'hosted-subpackage') {
    return {
      ok: true,
      target: resolveOutput ? resolveOutput.selectedTarget || resolveOutput.recommendedTarget || null : null,
      error: null,
    };
  }

  const targets = Array.isArray(resolveOutput.targets) ? resolveOutput.targets : [];
  const selectedTarget = resolveOutput.selectedTarget || null;
  if (explicitTarget && selectedTarget) {
    return { ok: true, target: selectedTarget, error: null };
  }

  if (targets.length <= 1 && selectedTarget) {
    return { ok: true, target: selectedTarget, error: null };
  }

  return {
    ok: false,
    target: null,
    error: {
      errorCode: 'TARGET_SELECTION_REQUIRED',
      error: 'Multiple hosted targets were found. Pass --target to continue.',
      recommendedTarget: resolveOutput.recommendedTarget || null,
      targets: targets.map((target) => ({
        weappType: target.weappType,
        scriptSuffix: target.scriptSuffix,
        devScript: target.devScript,
        devtoolsProjectPath: target.devtoolsProjectPath,
        subpackageRoot: target.subpackageRoot,
        isActiveCandidate: target.isActiveCandidate,
        selectionReason: target.selectionReason,
      })),
    },
  };
}

function ensureActionsSource(args) {
  if (args.actions_file && args.template) {
    throw new Error('Use either --actions-file or --template, not both');
  }
  if (args.actions_file) {
    return ['--actions-file', path.resolve(args.actions_file)];
  }
  if (args.template) {
    const templatePath = resolveTemplatePath(args.template, [
      `${args.template}.actions.json`,
      `${args.template}.json`,
      args.template,
    ]);
    const template = JSON.parse(fs.readFileSync(templatePath, 'utf8'));
    const resolved = applyTemplateVars(template, collectTemplateVars(args));
    return ['--actions-json', JSON.stringify(resolved)];
  }
  if (args.actions_json) {
    return ['--actions-json', args.actions_json];
  }
  return ['--actions-json', '[]'];
}

function ensurePreflightSource(args) {
  if (args.preflight_actions_file && args.preflight_template) {
    throw new Error('Use either --preflight-actions-file or --preflight-template, not both');
  }
  if (args.preflight_actions_file) {
    return ['--actions-file', path.resolve(args.preflight_actions_file)];
  }
  if (args.preflight_template) {
    const templatePath = resolveTemplatePath(args.preflight_template, [
      `${args.preflight_template}.actions.json`,
      `${args.preflight_template}.json`,
      args.preflight_template,
    ]);
    const template = JSON.parse(fs.readFileSync(templatePath, 'utf8'));
    const resolved = applyTemplateVars(template, collectTemplateVars(args));
    return ['--actions-json', JSON.stringify(resolved)];
  }
  if (args.preflight_actions_json) {
    return ['--actions-json', args.preflight_actions_json];
  }
  return null;
}

function parseTemplateValue(value) {
  try {
    return JSON.parse(value);
  } catch (error) {
    return value;
  }
}

function collectTemplateVars(args) {
  const vars = {};
  if (args.template_vars_json) {
    const parsed = JSON.parse(args.template_vars_json);
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      throw new Error('--template-vars-json must be a JSON object');
    }
    Object.assign(vars, parsed);
  }

  for (const entry of args.template_var || []) {
    const separator = entry.indexOf('=');
    if (separator <= 0) {
      throw new Error(`Invalid --template-var entry: ${entry}`);
    }
    const key = entry.slice(0, separator);
    const rawValue = entry.slice(separator + 1);
    vars[key] = parseTemplateValue(rawValue);
  }

  return vars;
}

function applyTemplateVars(value, vars) {
  if (Array.isArray(value)) {
    return value.map((item) => applyTemplateVars(item, vars));
  }

  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, applyTemplateVars(item, vars)])
    );
  }

  if (typeof value !== 'string') {
    return value;
  }

  const wholeMatch = value.match(/^\{\{([A-Z0-9_]+)\}\}$/);
  if (wholeMatch) {
    const variableName = wholeMatch[1];
    if (!Object.prototype.hasOwnProperty.call(vars, variableName)) {
      throw new Error(`Missing template variable: ${variableName}`);
    }
    return vars[variableName];
  }

  return value.replace(/\{\{([A-Z0-9_]+)\}\}/g, (match, variableName) => {
    if (!Object.prototype.hasOwnProperty.call(vars, variableName)) {
      throw new Error(`Missing template variable: ${variableName}`);
    }
    const replacement = vars[variableName];
    if (replacement == null) {
      return '';
    }
    if (typeof replacement === 'object') {
      return JSON.stringify(replacement);
    }
    return String(replacement);
  });
}

function resolveTemplatePath(templateName, candidates) {
  const templatesDir = path.resolve(__dirname, '..', 'templates');
  if (path.isAbsolute(templateName)) {
    if (!fs.existsSync(templateName)) {
      throw new Error(`Template not found: ${templateName}`);
    }
    return templateName;
  }

  for (const candidate of candidates) {
    const resolved = path.join(templatesDir, candidate);
    if (fs.existsSync(resolved)) {
      return resolved;
    }
  }

  throw new Error(`Template not found: ${templateName}`);
}

function listTemplates(suffix) {
  const templatesDir = path.resolve(__dirname, '..', 'templates');
  return fs.readdirSync(templatesDir)
    .filter((name) => name.endsWith(suffix))
    .map((name) => ({
      name: name.replace(suffix, ''),
      file: path.join(templatesDir, name),
    }))
    .sort((left, right) => left.name.localeCompare(right.name));
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function hashLockKey(value) {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16);
}

function buildSessionLockPath(projectPath, port) {
  return path.join('/tmp', `wechat-miniprogram-automator-lock-${hashLockKey(`${projectPath}:${port}`)}`);
}

function defaultAutomationPort(projectPath) {
  return 9400 + (Number.parseInt(hashLockKey(projectPath), 16) % 400);
}

function isPidAlive(pid) {
  if (!Number.isInteger(pid) || pid <= 0) {
    return false;
  }
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return false;
  }
}

function clearStaleLock(lockPath) {
  const ownerPath = path.join(lockPath, 'owner.json');
  try {
    const owner = JSON.parse(fs.readFileSync(ownerPath, 'utf8'));
    if (!isPidAlive(owner.pid)) {
      fs.rmSync(lockPath, { recursive: true, force: true });
      return true;
    }
  } catch (error) {
    if (error && error.code === 'ENOENT') {
      return true;
    }
    fs.rmSync(lockPath, { recursive: true, force: true });
    return true;
  }
  return false;
}

async function acquireSessionLock(projectPath, port, timeoutMs) {
  const lockPath = buildSessionLockPath(projectPath, port);
  const startedMs = Date.now();
  const owner = {
    pid: process.pid,
    projectPath,
    port,
    startedAt: new Date().toISOString(),
  };

  while (Date.now() - startedMs < timeoutMs) {
    try {
      fs.mkdirSync(lockPath);
      fs.writeFileSync(path.join(lockPath, 'owner.json'), JSON.stringify(owner, null, 2));
      return {
        path: lockPath,
        waitedMs: Date.now() - startedMs,
        release() {
          try {
            fs.rmSync(lockPath, { recursive: true, force: true });
          } catch (error) {
            // Best effort cleanup.
          }
        },
      };
    } catch (error) {
      if (error && error.code === 'ENOENT') {
        await sleep(50);
        continue;
      }
      if (!error || error.code !== 'EEXIST') {
        throw error;
      }
      if (clearStaleLock(lockPath)) {
        await sleep(50);
        continue;
      }
    }

    await sleep(250);
  }

  throw new Error(`Timed out waiting for session lock: ${lockPath}`);
}

function summarizeResolve(resolveOutput) {
  if (!resolveOutput || typeof resolveOutput !== 'object') {
    return null;
  }

  const summary = {
    kind: resolveOutput.kind || null,
    workspaceRoot: resolveOutput.workspaceRoot || null,
    selectionReason: resolveOutput.selectionReason || null,
  };

  if (resolveOutput.selectedTarget && resolveOutput.selectedTarget.weappType) {
    summary.selectedTarget = resolveOutput.selectedTarget.weappType;
  }

  if (resolveOutput.recommendedTarget && resolveOutput.recommendedTarget.weappType) {
    summary.recommendedTarget = resolveOutput.recommendedTarget.weappType;
  }

  if (Array.isArray(resolveOutput.targets)) {
    summary.candidates = resolveOutput.targets.map((target) => ({
      weappType: target.weappType,
      devScript: target.devScript,
      subpackageRoot: target.subpackageRoot,
      isActiveCandidate: Boolean(target.isActiveCandidate),
      selectionReason: target.selectionReason || null,
    }));
  }

  return summary;
}

function summarizeTarget(target) {
  if (!target || typeof target !== 'object') {
    return null;
  }

  return {
    weappType: target.weappType || null,
    devScript: target.devScript || null,
    devtoolsProjectPath: target.devtoolsProjectPath || null,
    hostProjectPath: target.hostProjectPath || null,
    subpackageRoot: target.subpackageRoot || null,
    isActiveCandidate: Boolean(target.isActiveCandidate),
    selectionReason: target.selectionReason || null,
  };
}

function summarizeBootstrap(bootstrap) {
  if (!bootstrap || typeof bootstrap !== 'object') {
    return null;
  }

  return {
    ok: Boolean(bootstrap.ok),
    projectPath: bootstrap.projectPath || null,
    port: bootstrap.port || null,
    timeoutMs: bootstrap.timeoutMs || null,
    retries: bootstrap.retries || null,
    portListeningBefore: Boolean(bootstrap.portListeningBefore),
    portReady: Boolean(bootstrap.portReady),
    reusedExistingSession: Boolean(bootstrap.reusedExistingSession),
    warnings: Array.isArray(bootstrap.warnings) ? bootstrap.warnings : [],
    hasCliErrors: Boolean(bootstrap.hasCliErrors),
  };
}

function summarizeProbe(probe) {
  if (!probe || typeof probe !== 'object') {
    return null;
  }

  return {
    ok: Boolean(probe.ok),
    connected: Boolean(probe.connected),
    skippedCurrentPage: Boolean(probe.skippedCurrentPage),
    currentPageAvailable: Boolean(probe.currentPageAvailable),
    elapsedMs: probe.elapsedMs || null,
    error: probe.error || null,
  };
}

function summarizeRunnerResult(result) {
  if (!result || typeof result !== 'object') {
    return null;
  }

  return {
    ok: Boolean(result.ok),
    error: result.error || null,
    failedActionType: result.failedAction ? result.failedAction.type : null,
    failedAction: result.failedAction || null,
    diagnostics: result.diagnostics || null,
    requestEventCount: typeof result.requestEventCount === 'number' ? result.requestEventCount : 0,
    requestTail: Array.isArray(result.requestTail) ? result.requestTail : [],
  };
}

function buildFlowArtifactIndex(payload) {
  const run = payload && payload.run;
  const index = {
    successScreenshots: [],
    successSnapshots: [],
    failureScreenshot: null,
    failureSnapshot: null,
    runnerTracePath: run && run.artifacts ? run.artifacts.tracePath || null : null,
    reportPath: payload && payload.artifacts ? payload.artifacts.reportPath || null : null,
  };

  if (!run || typeof run !== 'object') {
    return index;
  }

  if (run.ok && Array.isArray(run.results)) {
    for (const item of run.results) {
      if (item.type === 'screenshot' && item.value && item.value.path) {
        index.successScreenshots.push(item.value.path);
      }
      if (item.type === 'snapshot' && item.value && item.value.path) {
        index.successSnapshots.push(item.value.path);
      }
    }
  }

  if (!run.ok && run.diagnostics) {
    index.failureScreenshot = run.diagnostics.screenshotPath || null;
    index.failureSnapshot = run.diagnostics.snapshotPath || null;
  }

  return index;
}

function classifyRunFailure(run) {
  if (!run || typeof run !== 'object') {
    return 'assertion_failed';
  }

  const failedActionType = run.failedAction ? run.failedAction.type : null;
  const requestTail = Array.isArray(run.requestTail) ? run.requestTail : [];
  const hasRecentRequestFailure = requestTail.some((item) => item && item.ok === false);

  if (failedActionType === 'waitForRequest') {
    return 'request_failed';
  }
  if (failedActionType === 'waitForRoute') {
    return 'route_failed';
  }
  if (hasRecentRequestFailure && (failedActionType === 'waitForSelector' || failedActionType === 'waitForData')) {
    return 'request_failed';
  }
  if ([
    'waitForSelector',
    'tap',
    'input',
    'text',
    'attribute',
  ].includes(failedActionType)) {
    return 'selector_failed';
  }
  return 'assertion_failed';
}

function classifyFlowFailure(payload) {
  if (!payload || payload.ok) {
    return null;
  }

  switch (payload.phase) {
    case 'bootstrap':
      return 'bootstrap_failed';
    case 'probe':
      return 'probe_failed';
    case 'preflight':
      return 'environment_blocked';
    case 'run':
      return classifyRunFailure(payload.run);
    default:
      return 'assertion_failed';
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    printHelp();
    return;
  }

  if (args.list_templates) {
    const templates = listTemplates('.actions.json');
    process.stdout.write(`${args.json ? JSON.stringify(templates) : `${templates.map((item) => `${item.name}\t${item.file}`).join('\n')}\n`}`);
    return;
  }

  const baseDir = __dirname;
  const resolverPath = path.join(baseDir, 'resolve_wechat_project.cjs');
  const bootstrapPath = path.join(baseDir, 'ensure_devtools_session.cjs');
  const probePath = path.join(baseDir, 'probe_devtools_ws.cjs');
  const runnerPath = path.join(baseDir, 'run_automator.cjs');
  const actionSourceArgs = ensureActionsSource(args);
  const preflightSourceArgs = ensurePreflightSource(args);
  const startedAt = new Date().toISOString();
  const startedMs = Date.now();
  const artifacts = buildArtifacts(args);

  const resolveResult = runJsonScript(resolverPath, [
    '--cwd',
    args.cwd,
    ...(args.target ? ['--target', args.target] : []),
  ], { supportsJsonFlag: true });
  const resolveSummary = resolveResult.parsed ? summarizeResolve(resolveResult.parsed) : null;

  if (resolveResult.exitCode !== 0 || !resolveResult.parsed) {
    const payload = {
      ok: false,
      phase: 'resolve',
      startedAt,
      endedAt: new Date().toISOString(),
      durationMs: Date.now() - startedMs,
      artifacts,
      resolver: resolveResult,
      error: 'Resolver failed',
    };
    writeReport(artifacts.reportPath, payload);
    process.stdout.write(`${args.json ? JSON.stringify(payload) : JSON.stringify(payload, null, 2)}\n`);
    process.exitCode = 1;
    return;
  }

  const selection = normalizeSelection(resolveResult.parsed, args.target);
  if (!selection.ok) {
    const payload = {
      ok: false,
      phase: 'select_target',
      startedAt,
      endedAt: new Date().toISOString(),
      durationMs: Date.now() - startedMs,
      artifacts,
      resolve: resolveSummary,
      ...selection.error,
    };
    writeReport(artifacts.reportPath, payload);
    process.stdout.write(`${args.json ? JSON.stringify(payload) : JSON.stringify(payload, null, 2)}\n`);
    process.exitCode = 1;
    return;
  }

  const selectedTarget =
    selection.target ||
    (resolveResult.parsed.kind === 'standalone-miniprogram'
      ? {
          devtoolsProjectPath: resolveResult.parsed.devtoolsProjectPath,
          hostProjectPath: resolveResult.parsed.projectPath,
        }
      : null);
  const targetSummary = summarizeTarget(selectedTarget);
  const devtoolsProjectPath = selectedTarget && selectedTarget.devtoolsProjectPath;
  const port = args.port == null ? defaultAutomationPort(devtoolsProjectPath) : args.port;
  const wsEndpoint = `ws://127.0.0.1:${port}`;
  let sessionLock;
  try {
    sessionLock = await acquireSessionLock(devtoolsProjectPath, port, args.lock_timeout_ms);
  } catch (error) {
    const payload = {
      ok: false,
      phase: 'session_lock',
      startedAt,
      endedAt: new Date().toISOString(),
      durationMs: Date.now() - startedMs,
      artifacts,
      resolve: resolveSummary,
      target: targetSummary,
      error: error.message,
    };
    writeReport(artifacts.reportPath, payload);
    process.stdout.write(`${args.json ? JSON.stringify(payload) : JSON.stringify(payload, null, 2)}\n`);
    process.exitCode = 1;
    return;
  }

  try {
    const bootstrapResult = runJsonScript(bootstrapPath, [
      '--project-path',
      devtoolsProjectPath,
      '--port',
      String(port),
      '--timeout-ms',
      String(args.timeout_ms),
      '--retries',
      String(args.retries),
    ], { supportsJsonFlag: true });
    const bootstrapSummary = bootstrapResult.parsed ? summarizeBootstrap(bootstrapResult.parsed) : null;
    if (bootstrapResult.exitCode !== 0 || !bootstrapResult.parsed || !bootstrapResult.parsed.ok) {
      const fallback = collectPortFallback(devtoolsProjectPath, port, wsEndpoint);
      const payload = {
        ok: false,
        phase: 'bootstrap',
        startedAt,
        endedAt: new Date().toISOString(),
        durationMs: Date.now() - startedMs,
        artifacts,
        resolve: resolveSummary,
        target: targetSummary,
        bootstrap: bootstrapSummary || bootstrapResult.parsed || bootstrapResult,
        fallback,
        error: 'Bootstrap failed',
      };
      payload.failureType = classifyFlowFailure(payload);
      payload.artifactIndex = buildFlowArtifactIndex(payload);
      writeReport(artifacts.reportPath, payload);
      process.stdout.write(`${args.json ? JSON.stringify(payload) : JSON.stringify(payload, null, 2)}\n`);
      process.exitCode = 1;
      return;
    }

    const probeResult = runJsonScript(probePath, [
      '--ws-endpoint',
      wsEndpoint,
      '--timeout-ms',
      String(args.probe_timeout_ms),
      ...(args.skip_current_page_probe ? ['--skip-current-page'] : []),
    ], { supportsJsonFlag: true });
    const probeSummary = probeResult.parsed ? summarizeProbe(probeResult.parsed) : null;
    if (probeResult.exitCode !== 0 || !probeResult.parsed || !probeResult.parsed.ok) {
      const fallback = collectPortFallback(devtoolsProjectPath, port, wsEndpoint);
      const payload = {
        ok: false,
        phase: 'probe',
        startedAt,
        endedAt: new Date().toISOString(),
        durationMs: Date.now() - startedMs,
        artifacts,
        resolve: resolveSummary,
        target: targetSummary,
        bootstrap: bootstrapSummary,
        probe: probeSummary || probeResult.parsed || probeResult,
        fallback,
        error: 'Websocket probe failed',
      };
      payload.failureType = classifyFlowFailure(payload);
      payload.artifactIndex = buildFlowArtifactIndex(payload);
      writeReport(artifacts.reportPath, payload);
      process.stdout.write(`${args.json ? JSON.stringify(payload) : JSON.stringify(payload, null, 2)}\n`);
      process.exitCode = 1;
      return;
    }

    let preflightSummary = null;
    if (preflightSourceArgs) {
      const preflightResult = runJsonScript(runnerPath, [
        '--mode',
        'connect',
        '--ws-endpoint',
        wsEndpoint,
        '--artifacts-dir',
        path.join(artifacts.runDir, 'preflight-runner'),
        ...preflightSourceArgs,
      ], { supportsJsonFlag: false });
      preflightSummary = summarizeRunnerResult(preflightResult.parsed || preflightResult);
      if (preflightResult.exitCode !== 0 || !preflightResult.parsed || !preflightResult.parsed.ok) {
        const payload = {
          ok: false,
          phase: 'preflight',
          startedAt,
          endedAt: new Date().toISOString(),
          durationMs: Date.now() - startedMs,
          artifacts,
          resolve: resolveSummary,
          target: targetSummary,
          session: {
            mode: 'connect',
            wsEndpoint,
            port,
            lockPath: sessionLock.path,
            lockWaitedMs: sessionLock.waitedMs,
          },
          bootstrap: bootstrapSummary,
          probe: probeSummary,
          preflight: preflightResult.parsed || preflightResult,
          environmentBlocked: true,
          error: 'Preflight failed before the main flow. Treat this as an environment or readiness blocker until proven otherwise.',
        };
        payload.failureType = classifyFlowFailure(payload);
        payload.artifactIndex = buildFlowArtifactIndex(payload);
        writeReport(artifacts.reportPath, payload);
        process.stdout.write(`${args.json ? JSON.stringify(payload) : JSON.stringify(payload, null, 2)}\n`);
        process.exitCode = 1;
        return;
      }
    }

    const runnerArgs = [
      '--mode',
      'connect',
      '--ws-endpoint',
      wsEndpoint,
      '--artifacts-dir',
      path.join(artifacts.runDir, 'runner'),
      ...actionSourceArgs,
    ];
    const runnerResult = runJsonScript(runnerPath, runnerArgs, { supportsJsonFlag: false });

    const payload = {
      ok: runnerResult.exitCode === 0 && runnerResult.parsed ? Boolean(runnerResult.parsed.ok) : false,
      phase: runnerResult.exitCode === 0 ? 'completed' : 'run',
      startedAt,
      endedAt: new Date().toISOString(),
      durationMs: Date.now() - startedMs,
      artifacts,
      resolve: resolveSummary,
      target: targetSummary,
      session: {
        mode: 'connect',
        wsEndpoint,
        port,
        lockPath: sessionLock.path,
        lockWaitedMs: sessionLock.waitedMs,
      },
      bootstrap: bootstrapSummary,
      probe: probeSummary,
      preflight: preflightSummary,
      run: runnerResult.parsed || runnerResult,
    };
    payload.failureType = classifyFlowFailure(payload);
    payload.artifactIndex = buildFlowArtifactIndex(payload);

    writeReport(artifacts.reportPath, payload);
    process.stdout.write(`${args.json ? JSON.stringify(payload) : JSON.stringify(payload, null, 2)}\n`);
    if (!payload.ok) {
      process.exitCode = 1;
    }
  } finally {
    sessionLock.release();
  }
}

main().catch((error) => {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
});
