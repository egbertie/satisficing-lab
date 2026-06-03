#!/usr/bin/env node

const path = require('path');

function loadAutomator() {
  const candidates = [
    path.resolve(__dirname, '..', 'node_modules', 'miniprogram-automator'),
    path.resolve(__dirname, '..', '..', 'node_modules', 'miniprogram-automator'),
    'miniprogram-automator',
  ];

  for (const candidate of candidates) {
    try {
      return require(candidate);
    } catch (error) {
      if (error && error.code !== 'MODULE_NOT_FOUND') {
        throw error;
      }
    }
  }

  throw new Error(
    'miniprogram-automator is not installed. Run `npm install miniprogram-automator` first.'
  );
}

const automator = loadAutomator();

function printHelp() {
  const lines = [
    'Usage:',
    '  node probe_devtools_ws.cjs --ws-endpoint ws://127.0.0.1:9420',
    '',
    'Options:',
    '  --ws-endpoint <url>    DevTools websocket endpoint.',
    '  --timeout-ms <ms>      Probe timeout. Defaults to 5000.',
    '  --skip-current-page    Only verify websocket connectivity.',
    '  --json                 Print compact JSON only.',
    '  --help                 Show this help.',
  ];

  process.stdout.write(`${lines.join('\n')}\n`);
}

function parseArgs(argv) {
  const args = {
    timeout_ms: '5000',
    skip_current_page: false,
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

    if (token === '--skip-current-page') {
      args.skip_current_page = true;
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

  if (!args.ws_endpoint) {
    throw new Error('--ws-endpoint is required');
  }

  args.timeout_ms = Number(args.timeout_ms);
  if (!Number.isFinite(args.timeout_ms) || args.timeout_ms <= 0) {
    throw new Error('--timeout-ms must be a positive number');
  }

  return args;
}

function withTimeout(label, timeoutMs, promiseFactory) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`${label} timed out after ${timeoutMs}ms`));
    }, timeoutMs);

    Promise.resolve()
      .then(promiseFactory)
      .then((value) => {
        clearTimeout(timer);
        resolve(value);
      })
      .catch((error) => {
        clearTimeout(timer);
        reject(error);
      });
  });
}

async function disconnectWithTimeout(miniProgram, timeoutMs) {
  await withTimeout('disconnect', timeoutMs, async () => {
    await Promise.resolve(miniProgram.disconnect());
    return true;
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    printHelp();
    return;
  }

  let miniProgram = null;
  const startedAt = Date.now();
  const payload = {
    ok: false,
    wsEndpoint: args.ws_endpoint,
    timeoutMs: args.timeout_ms,
    skippedCurrentPage: args.skip_current_page,
    connected: false,
    currentPageAvailable: false,
    elapsedMs: 0,
    currentPage: null,
    error: null,
  };

  try {
    miniProgram = await withTimeout('connect', args.timeout_ms, () =>
      automator.connect({ wsEndpoint: args.ws_endpoint })
    );
    payload.connected = true;

    if (!args.skip_current_page) {
      try {
        const page = await withTimeout('currentPage', args.timeout_ms, () => miniProgram.currentPage());
        payload.currentPageAvailable = !!page;
        payload.currentPage = page
          ? {
              path: page.path,
              query: page.query,
            }
          : null;
      } catch (error) {
        payload.currentPageAvailable = false;
        payload.currentPage = null;
        payload.error = error.message;
      }
    }

    payload.ok = payload.connected;
  } catch (error) {
    payload.error = error.message;
  } finally {
    payload.elapsedMs = Date.now() - startedAt;
    if (miniProgram) {
      try {
        await disconnectWithTimeout(miniProgram, Math.min(args.timeout_ms, 2000));
      } catch (error) {
        // Ignore disconnect failures in the probe.
      }
    }
  }

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
