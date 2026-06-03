#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

function printHelp() {
  const lines = [
    'Usage:',
    '  node resolve_wechat_project.cjs [--cwd /abs/path] [--target tongcheng] [--json]',
    '',
    'Options:',
    '  --cwd <dir>        Working directory to inspect. Defaults to process.cwd().',
    '  --target <name>    Preferred host target for hosted subpackages.',
    '  --json             Print compact JSON only.',
    '  --help             Show this help.',
  ];

  process.stdout.write(`${lines.join('\n')}\n`);
}

function parseArgs(argv) {
  const args = {
    cwd: process.cwd(),
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

  args.cwd = path.resolve(args.cwd);
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

function isMiniProgramRoot(dirPath) {
  return fileExists(path.join(dirPath, 'app.json'));
}

function findMiniProgramRoot(startPath) {
  let current = path.resolve(startPath);

  while (true) {
    if (isMiniProgramRoot(current)) {
      return current;
    }

    const parent = path.dirname(current);
    if (parent === current) {
      return null;
    }
    current = parent;
  }
}

function findAncestors(startPath) {
  const items = [];
  let current = path.resolve(startPath);

  while (true) {
    items.push(current);
    const parent = path.dirname(current);
    if (parent === current) {
      return items;
    }
    current = parent;
  }
}

function findWorkspaceRoot(startPath) {
  let current = path.resolve(startPath);

  while (true) {
    if (fileExists(path.join(current, 'package.json'))) {
      return current;
    }

    const parent = path.dirname(current);
    if (parent === current) {
      return startPath;
    }
    current = parent;
  }
}

function safeRequire(modulePath) {
  delete require.cache[require.resolve(modulePath)];
  return require(modulePath);
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function listProcesses() {
  try {
    return execFileSync('ps', ['-axo', 'pid=,command='], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    })
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const match = line.match(/^(\d+)\s+(.*)$/);
        if (!match) {
          return null;
        }
        return {
          pid: Number(match[1]),
          command: match[2],
        };
      })
      .filter(Boolean);
  } catch (error) {
    return [];
  }
}

function collectTargetAliases(target) {
  return [
    target.weappType,
    target.scriptSuffix,
    target.publishKey,
    target.devScript,
    target.buildScript,
    target.publishScript,
  ].filter(Boolean);
}

function detectActiveTargets(targets) {
  const processes = listProcesses();

  return targets.map((target) => {
    const aliases = collectTargetAliases(target);
    const devScriptToken = target.devScript || null;
    const buildScriptToken = target.buildScript || null;
    const watchTypeToken = target.weappType || null;
    const matchedProcesses = [];

    for (const processInfo of processes) {
      const command = processInfo.command;
      let reason = null;

      if (devScriptToken && command.includes(devScriptToken)) {
        reason = `Matched running dev script ${devScriptToken}`;
      } else if (buildScriptToken && command.includes(`${buildScriptToken} --watch`)) {
        reason = `Matched running build watch ${buildScriptToken}`;
      } else if (
        watchTypeToken &&
        command.includes('taro build --type weapp') &&
        command.includes(` ${watchTypeToken} `) &&
        command.includes('--watch')
      ) {
        reason = `Matched running taro watch for ${watchTypeToken}`;
      } else if (aliases.some((alias) => command.includes(alias) && command.includes('--watch'))) {
        reason = `Matched watch command containing target alias`;
      }

      if (reason) {
        matchedProcesses.push({
          pid: processInfo.pid,
          command,
          reason,
        });
      }
    }

    return {
      ...target,
      isActiveCandidate: matchedProcesses.length > 0,
      selectionReason: matchedProcesses.length > 0 ? matchedProcesses[0].reason : null,
      matchedProcesses,
    };
  });
}

function selectRecommendedTarget(targets) {
  const activeTargets = targets.filter((target) => target.isActiveCandidate);
  if (activeTargets.length === 1) {
    return {
      target: activeTargets[0],
      reason: activeTargets[0].selectionReason || 'Matched one active watch target',
    };
  }

  if (targets.length === 1) {
    return {
      target: targets[0],
      reason: 'Only one hosted target was found',
    };
  }

  return {
    target: null,
    reason:
      activeTargets.length > 1
        ? 'Multiple active watch targets were detected; ask the user to choose'
        : 'Multiple hosted targets were detected; ask the user to choose',
  };
}

function resolveDevtoolsProject(miniProgramRoot) {
  const normalizedMiniRoot = path.resolve(miniProgramRoot);
  let bestMatch = null;

  for (const candidateDir of findAncestors(normalizedMiniRoot)) {
    const configPath = path.join(candidateDir, 'project.config.json');
    if (!fileExists(configPath)) {
      continue;
    }

    let config;
    try {
      config = readJson(configPath);
    } catch (error) {
      continue;
    }

    const declaredMiniRoot = config.miniprogramRoot || config.srcMiniprogramRoot || '.';
    const resolvedMiniRoot = path.resolve(candidateDir, declaredMiniRoot);
    if (resolvedMiniRoot !== normalizedMiniRoot) {
      continue;
    }

    const score =
      (config.appid ? 4 : 0) +
      (config.compileType ? 2 : 0) +
      ((config.miniprogramRoot || config.srcMiniprogramRoot) ? 1 : 0);

    if (!bestMatch || score > bestMatch.score) {
      bestMatch = {
        score,
        devtoolsProjectPath: candidateDir,
        devtoolsConfigPath: configPath,
        miniProgramRoot: normalizedMiniRoot,
      };
    }
  }

  if (bestMatch) {
    return {
      devtoolsProjectPath: bestMatch.devtoolsProjectPath,
      devtoolsConfigPath: bestMatch.devtoolsConfigPath,
      miniProgramRoot: bestMatch.miniProgramRoot,
    };
  }

  return {
    devtoolsProjectPath: normalizedMiniRoot,
    devtoolsConfigPath: fileExists(path.join(normalizedMiniRoot, 'project.config.json'))
      ? path.join(normalizedMiniRoot, 'project.config.json')
      : null,
    miniProgramRoot: normalizedMiniRoot,
  };
}

function extractWeappTypes(configSource) {
  const match = configSource.match(/const\s+outConfig\s*=\s*\{([\s\S]*?)\n\};/);
  if (!match) {
    return [];
  }

  const keys = [];
  const keyPattern = /^\s*([A-Za-z0-9_]+)\s*:/gm;
  let keyMatch = keyPattern.exec(match[1]);
  while (keyMatch) {
    keys.push(keyMatch[1]);
    keyMatch = keyPattern.exec(match[1]);
  }
  return [...new Set(keys)];
}

function loadTaroConfig(configPath, weappType, nodeEnv) {
  const previousArgv = process.argv.slice();
  const previousNodeEnv = process.env.NODE_ENV;
  const previousTaroEnv = process.env.TARO_ENV;
  const previousLog = console.log;

  try {
    process.argv = ['node', 'script', 'build', '--type', 'weapp', weappType];
    process.env.NODE_ENV = nodeEnv;
    process.env.TARO_ENV = 'weapp';
    console.log = () => {};

    const factory = safeRequire(configPath);
    const merge = (...items) => Object.assign({}, ...items);
    return factory(merge);
  } finally {
    process.argv = previousArgv;
    process.env.NODE_ENV = previousNodeEnv;
    process.env.TARO_ENV = previousTaroEnv;
    console.log = previousLog;
  }
}

function mapHostedTargets(workspaceRoot) {
  const packageJsonPath = path.join(workspaceRoot, 'package.json');
  const mpsConfigPath = path.join(workspaceRoot, '.mps.config.js');
  const taroConfigPath = path.join(workspaceRoot, 'config', 'index.js');

  if (!fileExists(packageJsonPath) || !fileExists(mpsConfigPath) || !fileExists(taroConfigPath)) {
    return null;
  }

  const packageJson = readJson(packageJsonPath);
  const scripts = packageJson.scripts || {};
  const mpsConfig = safeRequire(mpsConfigPath);
  const publishConfig = (((mpsConfig || {}).mps || {}).publish) || {};
  const configSource = fs.readFileSync(taroConfigPath, 'utf8');
  const weappTypes = extractWeappTypes(configSource);

  if (!weappTypes.length) {
    return null;
  }

  const targets = [];
  for (const weappType of weappTypes) {
    const devConfig = loadTaroConfig(taroConfigPath, weappType, 'development');
    const prodConfig = loadTaroConfig(taroConfigPath, weappType, 'production');
    const devOutputRoot = devConfig.outputRoot;
    const prodOutputRoot = prodConfig.outputRoot;

    if (!devOutputRoot) {
      continue;
    }

    const absOutputRoot = path.resolve(workspaceRoot, devOutputRoot);
    const hostProjectPath = findMiniProgramRoot(absOutputRoot);
    const devtoolsProject = hostProjectPath ? resolveDevtoolsProject(hostProjectPath) : null;
    const publishEntry = Object.entries(publishConfig).find(([, value]) => {
      return value && value.mpsHome && path.normalize(value.mpsHome) === path.normalize(prodOutputRoot);
    });

    const publishKey = publishEntry ? publishEntry[0] : null;
    const publishMeta = publishEntry ? publishEntry[1] : null;
    const scriptSuffix = publishKey ? publishKey.replace(/^weapp-/, '') : null;

    targets.push({
      weappType,
      scriptSuffix,
      publishKey,
      devScript: scriptSuffix && scripts[`dev:${publishKey}`] ? `dev:${publishKey}` : null,
      buildScript: scriptSuffix && scripts[`build:${publishKey}`] ? `build:${publishKey}` : null,
      publishScript: scriptSuffix && scripts[`publish:${publishKey}`] ? `publish:${publishKey}` : null,
      devOutputRoot: absOutputRoot,
      prodOutputRoot: prodOutputRoot ? path.resolve(workspaceRoot, prodOutputRoot) : null,
      hostProjectPath,
      devtoolsProjectPath: devtoolsProject ? devtoolsProject.devtoolsProjectPath : null,
      devtoolsConfigPath: devtoolsProject ? devtoolsProject.devtoolsConfigPath : null,
      subpackageRoot: hostProjectPath ? path.relative(hostProjectPath, absOutputRoot) : null,
      publishName: publishMeta && publishMeta.name ? publishMeta.name : null,
      publishPages: publishMeta && Array.isArray(publishMeta.pages) ? publishMeta.pages : [],
    });
  }

  return detectActiveTargets(targets.filter((target) => target.hostProjectPath));
}

function resolveProject(args) {
  const workspaceRoot = findWorkspaceRoot(args.cwd);
  const hostedTargets = mapHostedTargets(workspaceRoot);

  if (hostedTargets && hostedTargets.length) {
    const wanted = args.target ? String(args.target) : null;
    const explicitTarget =
      hostedTargets.find((item) => {
        if (!wanted) {
          return false;
        }
        return (
          item.weappType === wanted ||
          item.scriptSuffix === wanted ||
          item.publishKey === wanted ||
          item.devScript === wanted ||
          item.buildScript === wanted ||
          item.publishScript === wanted
        );
      }) || null;
    const recommendedTarget = selectRecommendedTarget(hostedTargets);
    const selectedTarget = explicitTarget || recommendedTarget.target || null;

    return {
      kind: 'hosted-subpackage',
      workspaceRoot,
      selectedTarget,
      recommendedTarget: recommendedTarget.target,
      selectionReason: explicitTarget
        ? 'Matched explicit --target argument'
        : recommendedTarget.reason,
      targets: hostedTargets,
    };
  }

  const miniProgramRoot = findMiniProgramRoot(args.cwd) || findMiniProgramRoot(workspaceRoot);
  if (miniProgramRoot) {
    const devtoolsProject = resolveDevtoolsProject(miniProgramRoot);
    return {
      kind: 'standalone-miniprogram',
      workspaceRoot,
      projectPath: miniProgramRoot,
      devtoolsProjectPath: devtoolsProject.devtoolsProjectPath,
      devtoolsConfigPath: devtoolsProject.devtoolsConfigPath,
    };
  }

  return {
    kind: 'unknown',
    workspaceRoot,
    reason: 'No app.json root or hosted-subpackage config was found.',
  };
}

function main() {
  try {
    const args = parseArgs(process.argv.slice(2));
    if (args.help) {
      printHelp();
      return;
    }

    const result = resolveProject(args);
    const payload = args.json ? JSON.stringify(result) : JSON.stringify(result, null, 2);
    process.stdout.write(`${payload}\n`);
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  }
}

main();
