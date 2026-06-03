#!/usr/bin/env node

const fs = require('fs');
const net = require('net');
const path = require('path');
const { spawnSync } = require('child_process');

function printHelp() {
  const lines = [
    'Usage:',
    '  node ensure_devtools_session.cjs --project-path /abs/project [--port 9420]',
    '',
    'Options:',
    '  --project-path <path>  DevTools project root containing project.config.json.',
    '  --cli-path <path>      Defaults to /Applications/wechatwebdevtools.app/Contents/MacOS/cli.',
    '  --port <number>        Automation websocket port. Defaults to 9420.',
    '  --timeout-ms <ms>      Time to wait for the automation port. Defaults to 10000.',
    '  --retries <n>          Number of bootstrap attempts. Defaults to 1.',
    '  --json                 Print compact JSON only.',
    '  --help                 Show this help.',
  ];

  process.stdout.write(`${lines.join('\n')}\n`);
}

function parseArgs(argv) {
  const args = {
    cli_path: '/Applications/wechatwebdevtools.app/Contents/MacOS/cli',
    port: '9420',
    timeout_ms: '10000',
    retries: '1',
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

  if (!args.project_path) {
    throw new Error('--project-path is required');
  }

  args.project_path = path.resolve(args.project_path);
  args.port = Number(args.port);
  args.timeout_ms = Number(args.timeout_ms);
  args.retries = Number(args.retries);
  if (!Number.isFinite(args.timeout_ms) || args.timeout_ms <= 0) {
    throw new Error('--timeout-ms must be a positive number');
  }
  if (!Number.isInteger(args.retries) || args.retries <= 0) {
    throw new Error('--retries must be a positive integer');
  }
  return args;
}

function fileExists(filePath) {
  try {
    fs.accessSync(filePath);
    return true;
  } catch (error) {
    return false;
  }
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function validateDevtoolsProjectRoot(projectPath) {
  const configPath = path.join(projectPath, 'project.config.json');
  if (!fileExists(configPath)) {
    return {
      ok: false,
      errorCode: 'MISSING_PROJECT_CONFIG',
      error: `project.config.json was not found under ${projectPath}`,
      configPath,
    };
  }

  let config;
  try {
    config = readJson(configPath);
  } catch (error) {
    return {
      ok: false,
      errorCode: 'INVALID_PROJECT_CONFIG_JSON',
      error: `project.config.json could not be parsed: ${error.message}`,
      configPath,
    };
  }

  const declaredMiniRoot = config.miniprogramRoot || config.srcMiniprogramRoot || '.';
  const resolvedMiniRoot = path.resolve(projectPath, declaredMiniRoot);
  const appJsonPath = path.join(resolvedMiniRoot, 'app.json');
  const hasAppJson = fileExists(appJsonPath);
  const hasDevtoolsSignals = Boolean(config.compileType || config.appid || config.miniprogramRoot || config.srcMiniprogramRoot);

  if (!hasAppJson) {
    return {
      ok: false,
      errorCode: 'MISSING_APP_JSON',
      error: `Resolved Mini Program root does not contain app.json: ${resolvedMiniRoot}`,
      configPath,
      resolvedMiniProgramRoot: resolvedMiniRoot,
    };
  }

  if (!hasDevtoolsSignals) {
    return {
      ok: false,
      errorCode: 'INVALID_DEVTOOLS_PROJECT_ROOT',
      error: `The path looks like a runtime Mini Program directory, not a DevTools project root: ${projectPath}`,
      configPath,
      resolvedMiniProgramRoot: resolvedMiniRoot,
    };
  }

  return {
    ok: true,
    configPath,
    resolvedMiniProgramRoot: resolvedMiniRoot,
    config,
  };
}

function isPortListening(port) {
  return new Promise((resolve) => {
    const socket = net.createConnection({ host: '127.0.0.1', port });
    let settled = false;

    function finish(value) {
      if (!settled) {
        settled = true;
        socket.destroy();
        resolve(value);
      }
    }

    socket.once('connect', () => finish(true));
    socket.once('error', () => finish(false));
    socket.setTimeout(1000, () => finish(false));
  });
}

function waitForPort(port, timeoutMs) {
  const startedAt = Date.now();

  return new Promise((resolve) => {
    function tryOnce() {
      const socket = net.createConnection({ host: '127.0.0.1', port });
      let settled = false;

      function finish(value) {
        if (!settled) {
          settled = true;
          socket.destroy();
          resolve(value);
        }
      }

      socket.once('connect', () => finish(true));
      socket.once('error', () => {
        if (Date.now() - startedAt >= timeoutMs) {
          finish(false);
          return;
        }
        setTimeout(tryOnce, 250);
      });
      socket.setTimeout(1000, () => {
        if (Date.now() - startedAt >= timeoutMs) {
          finish(false);
          return;
        }
        setTimeout(tryOnce, 250);
      });
    }

    tryOnce();
  });
}

function collectWarnings(lastAttempt, portListeningBefore, portReady, attempts) {
  const warnings = [];
  const stdout = lastAttempt.stdout || '';
  const stderr = lastAttempt.stderr || '';
  const combined = `${stdout}\n${stderr}`;
  const hasCliErrors = /^\[error\]/m.test(stdout) || /TypeError|✖ /m.test(combined);
  const retried = (attempts || []).length > 1;

  if (hasCliErrors) {
    warnings.push('CLI reported internal errors while bootstrapping DevTools');
  }
  if (retried) {
    warnings.push('Bootstrap required multiple attempts before it became ready');
  }
  if (lastAttempt.exitCode === 0 && portReady && (hasCliErrors || retried || !portListeningBefore) && warnings.length) {
    warnings.push('Session is usable, but bootstrap completed with warnings');
  }

  return [...new Set(warnings)];
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    printHelp();
    return;
  }

  const validation = validateDevtoolsProjectRoot(args.project_path);
  if (!validation.ok) {
    const payload = {
      ok: false,
      projectPath: args.project_path,
      cliPath: args.cli_path,
      port: args.port,
      timeoutMs: args.timeout_ms,
      retries: args.retries,
      errorCode: validation.errorCode,
      error: validation.error,
      configPath: validation.configPath || null,
      resolvedMiniProgramRoot: validation.resolvedMiniProgramRoot || null,
    };
    const output = args.json ? JSON.stringify(payload) : JSON.stringify(payload, null, 2);
    process.stdout.write(`${output}\n`);
    process.exitCode = 1;
    return;
  }

  const portListeningBefore = await isPortListening(args.port);
  const attempts = [];
  let result = null;
  let portReady = false;

  for (let attempt = 1; attempt <= args.retries; attempt += 1) {
    result = spawnSync(
      args.cli_path,
      ['auto', '--project', args.project_path, '--auto-port', String(args.port)],
      {
        encoding: 'utf8',
      }
    );

    portReady = result.status === 0 ? await waitForPort(args.port, args.timeout_ms) : false;
    attempts.push({
      attempt,
      exitCode: result.status,
      portReady,
      stdout: result.stdout || '',
      stderr: result.stderr || '',
    });

    if (result.status === 0 && portReady) {
      break;
    }
  }

  const lastAttempt = attempts[attempts.length - 1] || {
    exitCode: null,
    stdout: '',
    stderr: '',
  };
  const reusedExistingSession =
    portListeningBefore ||
    /trying to connect|already started/i.test(lastAttempt.stderr || '');
  const warnings = collectWarnings(lastAttempt, portListeningBefore, portReady, attempts);
  const payload = {
    ok: lastAttempt.exitCode === 0 && portReady,
    projectPath: args.project_path,
    cliPath: args.cli_path,
    port: args.port,
    timeoutMs: args.timeout_ms,
    retries: args.retries,
    configPath: validation.configPath,
    resolvedMiniProgramRoot: validation.resolvedMiniProgramRoot,
    attempts,
    portListeningBefore,
    portReady,
    reusedExistingSession,
    hasCliErrors: warnings.some((item) => item.includes('CLI reported internal errors')),
    warnings,
    exitCode: lastAttempt.exitCode,
    stdout: lastAttempt.stdout || '',
    stderr: lastAttempt.stderr || '',
  };

  const output = args.json ? JSON.stringify(payload) : JSON.stringify(payload, null, 2);
  process.stdout.write(`${output}\n`);

  if (!payload.ok) {
    process.exitCode = 1;
  }
}

main().catch((error) => {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
});
