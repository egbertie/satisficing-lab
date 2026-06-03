#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { EventEmitter } = require('events');

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
    '  node run_automator.cjs --mode launch --project-path /abs/project --actions-file /tmp/actions.json',
    '  node run_automator.cjs --mode connect --ws-endpoint ws://127.0.0.1:9420 --actions-file /tmp/actions.json',
    '',
    'Options:',
    '  --mode launch|connect',
    '  --project-path <path>',
    '  --cli-path <path>',
    '  --ws-endpoint <ws url>',
    '  --port <number>',
    '  --account <wechat account>',
    '  --ticket <ticket>',
    '  --cwd <dir>',
    '  --trust-project',
    '  --actions-file <json file>',
    '  --actions-json <json string>',
    '  --artifacts-dir <dir>',
    '  --keep-open',
    '  --help',
  ];

  process.stdout.write(`${lines.join('\n')}\n`);
}

function parseArgs(argv) {
  const args = {
    keepOpen: false,
    trustProject: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];

    if (token === '--help') {
      args.help = true;
      continue;
    }

    if (token === '--keep-open') {
      args.keepOpen = true;
      continue;
    }

    if (token === '--trust-project') {
      args.trustProject = true;
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

  return args;
}

function readActions(args) {
  if (args.actions_file) {
    return JSON.parse(fs.readFileSync(path.resolve(args.actions_file), 'utf8'));
  }

  if (args.actions_json) {
    return JSON.parse(args.actions_json);
  }

  return [];
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
  return dirPath;
}

function resolveArtifacts(args) {
  if (!args.artifacts_dir) {
    return null;
  }

  const rootDir = ensureDir(path.resolve(args.artifacts_dir));
  const diagnosticsDir = ensureDir(path.join(rootDir, 'diagnostics'));
  return {
    rootDir,
    diagnosticsDir,
    tracePath: path.join(rootDir, 'trace.json'),
  };
}

async function getPage(miniProgram) {
  const page = await miniProgram.currentPage();
  if (!page) {
    throw new Error('No current page is available');
  }
  return page;
}

async function resolveScopeRoot(page, action) {
  if (!action.scopeSelector && !action.scopeXpath && !action.scopeXPath) {
    return page;
  }

  const scopeXpath = action.scopeXPath || action.scopeXpath;
  if (action.scopeSelector) {
    if (Number.isInteger(action.scopeSelectorIndex) && action.scopeSelectorIndex >= 0) {
      const elements = await page.$$(action.scopeSelector);
      const element = elements[action.scopeSelectorIndex];
      if (!element) {
        throw new Error(
          `Scope selector index out of range: ${action.scopeSelector} [${action.scopeSelectorIndex}]`
        );
      }
      return element;
    }

    const element = await page.$(action.scopeSelector);
    if (!element) {
      throw new Error(`Scope selector not found: ${action.scopeSelector}`);
    }
    return element;
  }

  const element = await page.xpath(scopeXpath);
  if (!element) {
    throw new Error(`Scope XPath not found: ${scopeXpath}`);
  }
  return element;
}

async function filterElementsByAction(elements, action) {
  let filtered = Array.isArray(elements) ? elements : [];

  if (typeof action.selectorText === 'string' && action.selectorText) {
    const exact = action.selectorTextExact === true;
    const matches = [];
    for (const element of filtered) {
      const textResult = await withBestEffortTimeout(500, async () => await element.text());
      if (!textResult.ok || typeof textResult.value !== 'string') {
        continue;
      }
      const haystack = exact ? textResult.value : textResult.value.toLowerCase();
      const needle = exact ? action.selectorText : action.selectorText.toLowerCase();
      if (exact ? haystack === needle : haystack.includes(needle)) {
        matches.push(element);
      }
    }
    filtered = matches;
  }

  if (typeof action.selectorAttributeName === 'string' && action.selectorAttributeName) {
    const exact = action.selectorAttributeExact !== false;
    const expected = Object.prototype.hasOwnProperty.call(action, 'selectorAttributeValue')
      ? String(action.selectorAttributeValue)
      : null;
    const matches = [];
    for (const element of filtered) {
      const attributeResult = await withBestEffortTimeout(
        500,
        async () => await element.attribute(action.selectorAttributeName)
      );
      if (!attributeResult.ok || typeof attributeResult.value !== 'string') {
        continue;
      }
      if (expected == null) {
        matches.push(element);
        continue;
      }
      const haystack = exact ? attributeResult.value : attributeResult.value.toLowerCase();
      const needle = exact ? expected : expected.toLowerCase();
      if (exact ? haystack === needle : haystack.includes(needle)) {
        matches.push(element);
      }
    }
    filtered = matches;
  }

  return filtered;
}

async function resolveElement(page, action) {
  const scopeRoot = await resolveScopeRoot(page, action);
  if (action.selector) {
    const elements = await filterElementsByAction(await scopeRoot.$$(action.selector), action);
    if (Number.isInteger(action.selectorIndex) && action.selectorIndex >= 0) {
      const element = elements[action.selectorIndex];
      if (!element) {
        throw new Error(
          `Selector index out of range: ${action.selector} [${action.selectorIndex}]`
        );
      }
      return element;
    }

    const element = elements[0];
    if (!element) {
      throw new Error(`Selector not found: ${action.selector}`);
    }
    return element;
  }

  if (action.xpath) {
    if (scopeRoot !== page) {
      throw new Error('Scoped xpath lookup is not supported; use scopeSelector + selector');
    }
    const element = await page.xpath(action.xpath);
    if (!element) {
      throw new Error(`XPath not found: ${action.xpath}`);
    }
    return element;
  }

  throw new Error(`Action ${action.type} requires selector or xpath`);
}

function simplifyPage(page) {
  if (!page) {
    return null;
  }

  return {
    path: page.path,
    query: page.query,
  };
}

function truncateString(value, maxLength = 500) {
  if (typeof value !== 'string') {
    return value;
  }
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength)}...`;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isPlainObject(value) {
  return value != null && typeof value === 'object' && !Array.isArray(value);
}

function matchesSubset(actual, expected) {
  if (!isPlainObject(expected)) {
    return actual === expected;
  }
  if (!isPlainObject(actual)) {
    return false;
  }

  return Object.entries(expected).every(([key, value]) => matchesSubset(actual[key], value));
}

function getByPath(value, targetPath) {
  if (!targetPath) {
    return value;
  }

  return String(targetPath)
    .split('.')
    .filter(Boolean)
    .reduce((current, segment) => (current == null ? undefined : current[segment]), value);
}

function describeValue(value) {
  if (value === undefined) {
    return {
      found: false,
      type: 'undefined',
      value: null,
    };
  }

  if (value === null) {
    return {
      found: true,
      type: 'null',
      value: null,
    };
  }

  if (Array.isArray(value)) {
    return {
      found: true,
      type: 'array',
      value,
    };
  }

  return {
    found: true,
    type: typeof value,
    value,
  };
}

async function waitForRoute(miniProgram, action) {
  const timeoutMs = typeof action.timeoutMs === 'number' && action.timeoutMs > 0 ? action.timeoutMs : 5000;
  const pollMs = typeof action.pollMs === 'number' && action.pollMs > 0 ? action.pollMs : 200;
  const expectedPath = action.path || action.url;
  if (!expectedPath) {
    throw new Error('waitForRoute action requires path or url');
  }

  const startedAt = Date.now();
  let lastPage = null;
  while (Date.now() - startedAt <= timeoutMs) {
    const page = await miniProgram.currentPage();
    lastPage = simplifyPage(page);
    const pathMatches = lastPage && lastPage.path === expectedPath.replace(/^\//, '');
    const queryMatches = !action.query || matchesSubset(lastPage ? lastPage.query : null, action.query);
    if (pathMatches && queryMatches) {
      return {
        path: lastPage.path,
        query: lastPage.query,
        waitedMs: Date.now() - startedAt,
      };
    }
    await sleep(pollMs);
  }

  throw new Error(
    `waitForRoute timed out after ${timeoutMs}ms waiting for ${expectedPath}`
  );
}

async function waitForData(miniProgram, action) {
  const timeoutMs = typeof action.timeoutMs === 'number' && action.timeoutMs > 0 ? action.timeoutMs : 5000;
  const pollMs = typeof action.pollMs === 'number' && action.pollMs > 0 ? action.pollMs : 200;
  const dataPath = action.path;
  if (!dataPath) {
    throw new Error('waitForData action requires path');
  }

  const startedAt = Date.now();
  let lastValue;
  while (Date.now() - startedAt <= timeoutMs) {
    const page = await getPage(miniProgram);
    lastValue = await page.data(dataPath);
    const truthyMatched = action.truthy === true ? Boolean(lastValue) : false;
    const equalsMatched = Object.prototype.hasOwnProperty.call(action, 'equals')
      ? matchesSubset(lastValue, action.equals)
      : false;
    const matched =
      action.truthy === true
        ? truthyMatched
        : Object.prototype.hasOwnProperty.call(action, 'equals')
          ? equalsMatched
          : Boolean(lastValue);

    if (matched) {
      return {
        path: dataPath,
        value: lastValue,
        waitedMs: Date.now() - startedAt,
      };
    }
    await sleep(pollMs);
  }

  throw new Error(
    `waitForData timed out after ${timeoutMs}ms waiting for ${dataPath}; last value: ${JSON.stringify(lastValue)}`
  );
}

async function waitForSelector(miniProgram, action) {
  const timeoutMs = typeof action.timeoutMs === 'number' && action.timeoutMs > 0 ? action.timeoutMs : 5000;
  const pollMs = typeof action.pollMs === 'number' && action.pollMs > 0 ? action.pollMs : 200;
  if (!action.selector && !action.xpath) {
    throw new Error('waitForSelector action requires selector or xpath');
  }

  const startedAt = Date.now();
  while (Date.now() - startedAt <= timeoutMs) {
    const page = await getPage(miniProgram);
    const scopeRoot = await resolveScopeRoot(page, action);
    const result = action.selector
      ? (await filterElementsByAction(await scopeRoot.$$(action.selector), action))[0] || null
      : scopeRoot === page
        ? await page.xpath(action.xpath)
        : null;
    if (result) {
      return {
        matched: action.selector || action.xpath,
        waitedMs: Date.now() - startedAt,
      };
    }
    await sleep(pollMs);
  }

  throw new Error(
    `waitForSelector timed out after ${timeoutMs}ms waiting for ${action.selector || action.xpath}`
  );
}

function normalizeRequestEvent(event) {
  if (!event || typeof event !== 'object') {
    return null;
  }

  return {
    method: typeof event.method === 'string' && event.method ? event.method : 'GET',
    url: typeof event.url === 'string' ? event.url : '',
    startAt: typeof event.startAt === 'string' ? event.startAt : null,
    endAt: typeof event.endAt === 'string' ? event.endAt : null,
    durationMs: typeof event.durationMs === 'number' ? event.durationMs : null,
    statusCode: typeof event.statusCode === 'number' ? event.statusCode : null,
    ok: typeof event.ok === 'boolean' ? event.ok : false,
    error: typeof event.error === 'string' ? truncateString(event.error, 300) : null,
  };
}

function matchesRequestEvent(event, action) {
  if (!event) {
    return false;
  }

  if (typeof action.url === 'string' && action.url && event.url !== action.url) {
    return false;
  }

  if (typeof action.urlIncludes === 'string' && action.urlIncludes && !event.url.includes(action.urlIncludes)) {
    return false;
  }

  if (typeof action.method === 'string' && action.method && event.method !== String(action.method).toUpperCase()) {
    return false;
  }

  if (typeof action.ok === 'boolean' && event.ok !== action.ok) {
    return false;
  }

  if (typeof action.statusCode === 'number' && event.statusCode !== action.statusCode) {
    return false;
  }

  return true;
}

async function waitForRequest(telemetry, action) {
  if (!telemetry || !Array.isArray(telemetry.requestEvents)) {
    throw new Error('waitForRequest action requires request telemetry');
  }

  const timeoutMs = typeof action.timeoutMs === 'number' && action.timeoutMs > 0 ? action.timeoutMs : 5000;
  const pollMs = typeof action.pollMs === 'number' && action.pollMs > 0 ? action.pollMs : 200;
  const startedAt = Date.now();
  let lastMatched = null;

  while (Date.now() - startedAt <= timeoutMs) {
    for (let index = telemetry.requestEvents.length - 1; index >= 0; index -= 1) {
      const event = telemetry.requestEvents[index];
      if (matchesRequestEvent(event, action)) {
        lastMatched = event;
        break;
      }
    }
    if (lastMatched) {
      return {
        waitedMs: Date.now() - startedAt,
        request: lastMatched,
      };
    }
    await sleep(pollMs);
  }

  throw new Error(
    `waitForRequest timed out after ${timeoutMs}ms waiting for request ${JSON.stringify({
      url: action.url || null,
      urlIncludes: action.urlIncludes || null,
      method: action.method || null,
      ok: typeof action.ok === 'boolean' ? action.ok : null,
      statusCode: typeof action.statusCode === 'number' ? action.statusCode : null,
    })}`
  );
}

async function buildSnapshot(miniProgram, action = {}) {
  const page = await getPage(miniProgram);
  const fullData = await page.data();
  const snapshot = {
    currentPage: simplifyPage(page),
    pageStack: simplifyPageStack(await miniProgram.pageStack()),
  };

  if (Array.isArray(action.dataPaths) && action.dataPaths.length > 0) {
    const data = {};
    const dataMeta = {};
    let hasDefinedValue = false;

    for (const dataPath of action.dataPaths) {
      const described = describeValue(await page.data(dataPath));
      data[dataPath] = described.value;
      dataMeta[dataPath] = {
        found: described.found,
        type: described.type,
      };
      if (described.found) {
        hasDefinedValue = true;
      }
    }

    snapshot.data = data;
    snapshot.dataMeta = dataMeta;

    // Taro React pages commonly expose a render tree under `root` while hook state
    // is not addressable as top-level page.data() keys.
    if (!hasDefinedValue && fullData && typeof fullData === 'object' && fullData.root) {
      snapshot.rootDataAvailable = true;
      snapshot.dataTree = await inspectDataTree(miniProgram, {
        path: 'root',
        limit: Number.isInteger(action.dataTreeLimit) && action.dataTreeLimit > 0
          ? action.dataTreeLimit
          : 30,
      });
    }
  } else if (action.includeFullData === true) {
    snapshot.data = fullData;
  }

  if (action.path) {
    const snapshotPath = path.resolve(action.path);
    fs.writeFileSync(snapshotPath, JSON.stringify(snapshot, null, 2));
    snapshot.path = snapshotPath;
  }

  return snapshot;
}

async function listElements(page, action) {
  const scopeRoot = await resolveScopeRoot(page, action);
  if (action.selector) {
    return await filterElementsByAction(await scopeRoot.$$(action.selector), action);
  }
  if (action.xpath) {
    if (scopeRoot !== page) {
      throw new Error('Scoped xpath lookup is not supported; use scopeSelector + selector');
    }
    return await page.getElementsByXpath(action.xpath);
  }
  throw new Error(`${action.type} action requires selector or xpath`);
}

async function summarizeElement(element, action = {}) {
  const summary = {
    tagName: element.tagName,
  };

  const textResult = await withBestEffortTimeout(500, async () => await element.text());
  summary.text = textResult.ok ? textResult.value : null;
  summary.textError = textResult.ok ? null : textResult.error;

  const attributes = Array.isArray(action.attributes) && action.attributes.length > 0
    ? action.attributes
    : ['class', 'id'];
  if (attributes.length > 0) {
    const attrs = {};
    for (const attributeName of attributes) {
      const attributeResult = await withBestEffortTimeout(500, async () => await element.attribute(attributeName));
      attrs[attributeName] = attributeResult.ok ? attributeResult.value : null;
    }
    summary.attributes = attrs;
  }

  if (action.includeSize) {
    const sizeResult = await withBestEffortTimeout(500, async () => await element.size());
    summary.size = sizeResult.ok ? sizeResult.value : null;
  }

  if (action.includeWxml) {
    const wxmlResult = await withBestEffortTimeout(500, async () => await element.outerWxml());
    summary.wxml = wxmlResult.ok ? wxmlResult.value : null;
  }

  return summary;
}

async function collectSearchFields(element, action = {}) {
  const fields = [];

  const textResult = await withBestEffortTimeout(500, async () => await element.text());
  if (textResult.ok && typeof textResult.value === 'string') {
    fields.push({
      field: 'text',
      value: textResult.value,
    });
  }

  const searchAttributes = Array.isArray(action.searchAttributes) && action.searchAttributes.length > 0
    ? action.searchAttributes
    : ['class', 'id'];
  for (const attributeName of searchAttributes) {
    const attributeResult = await withBestEffortTimeout(500, async () => await element.attribute(attributeName));
    if (attributeResult.ok && typeof attributeResult.value === 'string' && attributeResult.value) {
      fields.push({
        field: `attribute:${attributeName}`,
        value: attributeResult.value,
      });
    }
  }

  if (action.searchWxml === true) {
    const wxmlResult = await withBestEffortTimeout(500, async () => await element.outerWxml());
    if (wxmlResult.ok && typeof wxmlResult.value === 'string') {
      fields.push({
        field: 'wxml',
        value: wxmlResult.value,
      });
    }
  }

  return fields;
}

async function inspectElements(miniProgram, action) {
  const page = await getPage(miniProgram);
  const elements = await listElements(page, action);
  const limit = Number.isInteger(action.limit) && action.limit > 0 ? action.limit : elements.length;
  const summaries = [];

  for (const element of elements.slice(0, limit)) {
    summaries.push(await summarizeElement(element, action));
  }

  return {
    matched: elements.length,
    returned: summaries.length,
    elements: summaries,
  };
}

async function findByText(miniProgram, action) {
  const needle = action.text;
  if (typeof needle !== 'string' || !needle) {
    throw new Error('findByText action requires text');
  }

  const page = await getPage(miniProgram);
  const queryAction = Object.assign({ selector: '*' }, action);
  const elements = await listElements(page, queryAction);
  const limit = Number.isInteger(action.limit) && action.limit > 0 ? action.limit : elements.length;
  const matches = [];
  const normalizedNeedle = action.exact ? needle : needle.toLowerCase();

  for (const element of elements) {
    const fields = await collectSearchFields(element, action);
    const matchedField = fields.find(({ value }) => {
      const haystack = action.exact ? value : value.toLowerCase();
      return action.exact ? haystack === normalizedNeedle : haystack.includes(normalizedNeedle);
    });
    if (!matchedField) {
      continue;
    }

    const summary = await summarizeElement(element, action);
    summary.matchedField = matchedField.field;
    summary.matchedValue = matchedField.value;
    matches.push(summary);
    if (matches.length >= limit) {
      break;
    }
  }

  return {
    matched: matches.length,
    text: needle,
    elements: matches,
  };
}

function summarizeDataNode(node, path) {
  if (node == null || typeof node !== 'object') {
    return null;
  }

  return {
    path,
    className: typeof node.cl === 'string' ? node.cl : null,
    text: typeof node.v === 'string' ? node.v : null,
    sid: typeof node.sid === 'string' ? node.sid : null,
    childCount: Array.isArray(node.cn) ? node.cn.length : 0,
  };
}

function walkDataTree(node, path, visitor) {
  const summary = summarizeDataNode(node, path);
  if (summary) {
    visitor(summary, node);
  }

  if (!node || typeof node !== 'object') {
    return;
  }

  if (Array.isArray(node)) {
    node.forEach((child, index) => {
      walkDataTree(child, `${path}[${index}]`, visitor);
    });
    return;
  }

  if (Array.isArray(node.cn)) {
    node.cn.forEach((child, index) => {
      walkDataTree(child, `${path}.cn[${index}]`, visitor);
    });
  }
}

function tokenizeClassName(className) {
  return String(className || '')
    .split(/\s+/)
    .map((token) => token.trim())
    .filter(Boolean);
}

async function inspectDataTree(miniProgram, action) {
  const page = await getPage(miniProgram);
  const rootPath = action.path || 'root';
  const fullData = await page.data();
  const data = getByPath(fullData, rootPath);
  const nodes = [];
  const limit = Number.isInteger(action.limit) && action.limit > 0 ? action.limit : 50;

  walkDataTree(data, rootPath, (summary) => {
    if (nodes.length < limit) {
      nodes.push(summary);
    }
  });

  return {
    rootPath,
    returned: nodes.length,
    nodes,
  };
}

async function findInDataTree(miniProgram, action) {
  const needle = action.text;
  if (typeof needle !== 'string' || !needle) {
    throw new Error('findInDataTree action requires text');
  }

  const page = await getPage(miniProgram);
  const rootPath = action.path || 'root';
  const fullData = await page.data();
  const data = getByPath(fullData, rootPath);
  const matches = [];
  const limit = Number.isInteger(action.limit) && action.limit > 0 ? action.limit : 20;
  const normalizedNeedle = action.exact ? needle : needle.toLowerCase();

  walkDataTree(data, rootPath, (summary) => {
    if (matches.length >= limit) {
      return;
    }
    const candidates = [summary.className, summary.text, summary.sid].filter((value) => typeof value === 'string' && value);
    const matchedValue = candidates.find((value) => {
      const haystack = action.exact ? value : value.toLowerCase();
      return action.exact ? haystack === normalizedNeedle : haystack.includes(normalizedNeedle);
    });
    if (!matchedValue) {
      return;
    }
    matches.push(Object.assign({}, summary, {
      matchedValue,
    }));
  });

  return {
    rootPath,
    matched: matches.length,
    text: needle,
    nodes: matches,
  };
}

async function suggestSelectors(miniProgram, action) {
  const page = await getPage(miniProgram);
  const rootPath = action.path || 'root';
  const fullData = await page.data();
  const data = getByPath(fullData, rootPath);
  const limit = Number.isInteger(action.limit) && action.limit > 0 ? action.limit : 20;
  const minCount = Number.isInteger(action.minCount) && action.minCount > 0 ? action.minCount : 1;
  const classStats = new Map();

  walkDataTree(data, rootPath, (summary) => {
    for (const className of tokenizeClassName(summary.className)) {
      if (!classStats.has(className)) {
        classStats.set(className, {
          className,
          count: 0,
          samplePaths: [],
        });
      }
      const entry = classStats.get(className);
      entry.count += 1;
      if (entry.samplePaths.length < 3) {
        entry.samplePaths.push(summary.path);
      }
    }
  });

  const ranked = Array.from(classStats.values())
    .filter((entry) => entry.count >= minCount)
    .sort((left, right) => right.count - left.count || left.className.localeCompare(right.className))
    .slice(0, limit);

  const suggestions = [];
  for (const entry of ranked) {
    const selector = `.${entry.className}`;
    const elements = await withBestEffortTimeout(1000, async () => await page.$$(selector));
    suggestions.push({
      selector,
      className: entry.className,
      occurrencesInData: entry.count,
      matchedElements: elements.ok && Array.isArray(elements.value) ? elements.value.length : 0,
      samplePaths: entry.samplePaths,
    });
  }

  return {
    rootPath,
    returned: suggestions.length,
    suggestions,
  };
}

async function setGlobalData(miniProgram, action) {
  if (typeof action.path === 'string' && action.path) {
    return await miniProgram.evaluate((targetPath, nextValue) => {
      const segments = String(targetPath).split('.').filter(Boolean);
      const app = getApp();
      let current = app.globalData || (app.globalData = {});
      for (let index = 0; index < segments.length - 1; index += 1) {
        const segment = segments[index];
        const value = current[segment];
        if (value == null || typeof value !== 'object' || Array.isArray(value)) {
          current[segment] = {};
        }
        current = current[segment];
      }
      current[segments[segments.length - 1]] = nextValue;
      return app.globalData;
    }, action.path, action.value);
  }

  if (isPlainObject(action.data)) {
    return await miniProgram.evaluate((nextData) => {
      const app = getApp();
      app.globalData = Object.assign({}, app.globalData || {}, nextData);
      return app.globalData;
    }, action.data);
  }

  throw new Error('setGlobalData action requires path/value or data');
}

async function getGlobalData(miniProgram, action) {
  return await miniProgram.evaluate((targetPath) => {
    const app = getApp();
    const globalData = app.globalData || {};
    if (!targetPath) {
      return globalData;
    }
    return String(targetPath)
      .split('.')
      .filter(Boolean)
      .reduce((current, segment) => (current == null ? undefined : current[segment]), globalData);
  }, action.path || null);
}

async function callAppMethod(miniProgram, action) {
  if (typeof action.method !== 'string' || !action.method) {
    throw new Error('callAppMethod action requires method');
  }

  return await miniProgram.evaluate((methodPath, args) => {
    const app = getApp();
    const target = String(methodPath)
      .split('.')
      .filter(Boolean)
      .reduce((current, segment) => (current == null ? undefined : current[segment]), app);
    if (typeof target !== 'function') {
      throw new Error(`App method not found: ${methodPath}`);
    }
    return target.apply(app, Array.isArray(args) ? args : []);
  }, action.method, action.args || []);
}

async function runAction(miniProgram, action, context = {}) {
  switch (action.type) {
    case 'reLaunch':
    case 'navigateTo':
    case 'redirectTo':
    case 'switchTab': {
      const page = await miniProgram[action.type](action.url);
      return simplifyPage(page);
    }
    case 'navigateBack': {
      const page = await miniProgram.navigateBack();
      return simplifyPage(page);
    }
    case 'wait': {
      const page = await getPage(miniProgram);
      if (typeof action.ms === 'number') {
        await page.waitFor(action.ms);
        return { waitedMs: action.ms };
      }
      if (typeof action.condition === 'string') {
        await page.waitFor(action.condition);
        return { waitedForCondition: action.condition };
      }
      throw new Error('wait action requires ms or condition');
    }
    case 'scrollTo': {
      const scrollTop = Number.isFinite(action.top) ? action.top : action.scrollTop;
      if (!Number.isFinite(scrollTop)) {
        throw new Error('scrollTo action requires top or scrollTop');
      }
      await miniProgram.pageScrollTo(scrollTop);
      if (typeof action.waitMs === 'number' && action.waitMs > 0) {
        await sleep(action.waitMs);
      }
      return {
        scrollTop,
        waitedMs: typeof action.waitMs === 'number' && action.waitMs > 0 ? action.waitMs : 0,
      };
    }
    case 'waitForRoute': {
      return await waitForRoute(miniProgram, action);
    }
    case 'waitForData': {
      return await waitForData(miniProgram, action);
    }
    case 'waitForSelector': {
      return await waitForSelector(miniProgram, action);
    }
    case 'waitForRequest': {
      return await waitForRequest(context.telemetry, action);
    }
    case 'snapshot': {
      return await buildSnapshot(miniProgram, action);
    }
    case 'inspectElements': {
      return await inspectElements(miniProgram, action);
    }
    case 'findByText': {
      return await findByText(miniProgram, action);
    }
    case 'inspectDataTree': {
      return await inspectDataTree(miniProgram, action);
    }
    case 'findInDataTree': {
      return await findInDataTree(miniProgram, action);
    }
    case 'suggestSelectors': {
      return await suggestSelectors(miniProgram, action);
    }
    case 'tap': {
      const page = await getPage(miniProgram);
      const element = await resolveElement(page, action);
      await element.tap();
      return { tapped: action.selector || action.xpath };
    }
    case 'input': {
      const page = await getPage(miniProgram);
      const element = await resolveElement(page, action);
      await element.input(String(action.value ?? ''));
      return { input: action.selector || action.xpath };
    }
    case 'text': {
      const page = await getPage(miniProgram);
      const element = await resolveElement(page, action);
      return { text: await element.text() };
    }
    case 'attribute': {
      const page = await getPage(miniProgram);
      const element = await resolveElement(page, action);
      return { [action.name]: await element.attribute(action.name) };
    }
    case 'data': {
      const page = await getPage(miniProgram);
      return await page.data(action.path);
    }
    case 'setData': {
      const page = await getPage(miniProgram);
      await page.setData(action.data || {});
      return { updated: true };
    }
    case 'callMethod': {
      const page = await getPage(miniProgram);
      return await page.callMethod(action.method, ...(action.args || []));
    }
    case 'setGlobalData': {
      return await setGlobalData(miniProgram, action);
    }
    case 'getGlobalData': {
      return await getGlobalData(miniProgram, action);
    }
    case 'callAppMethod': {
      return await callAppMethod(miniProgram, action);
    }
    case 'callWxMethod': {
      return await miniProgram.callWxMethod(action.method, ...(action.args || []));
    }
    case 'setStorage': {
      if (typeof action.key !== 'string' || !action.key) {
        throw new Error('setStorage action requires key');
      }
      await miniProgram.callWxMethod('setStorageSync', action.key, action.value);
      return {
        key: action.key,
        stored: true,
      };
    }
    case 'getStorage': {
      if (typeof action.key !== 'string' || !action.key) {
        throw new Error('getStorage action requires key');
      }
      return {
        key: action.key,
        value: await miniProgram.callWxMethod('getStorageSync', action.key),
      };
    }
    case 'clearStorage': {
      await miniProgram.callWxMethod('clearStorageSync');
      return { cleared: true };
    }
    case 'mockWxMethod': {
      await miniProgram.mockWxMethod(action.method, action.result, ...(action.args || []));
      return { mocked: action.method };
    }
    case 'restoreWxMethod': {
      await miniProgram.restoreWxMethod(action.method);
      return { restored: action.method };
    }
    case 'screenshot': {
      const value = await miniProgram.screenshot({ path: action.path });
      return { path: action.path || value || null };
    }
    default:
      throw new Error(`Unsupported action type: ${action.type}`);
  }
}

async function openMiniProgram(args) {
  if (args.mode === 'launch') {
    if (!args.project_path) {
      throw new Error('--project-path is required in launch mode');
    }

    const launchOptions = {
      projectPath: args.project_path,
      trustProject: args.trustProject,
    };

    if (args.cli_path) {
      launchOptions.cliPath = args.cli_path;
    }
    if (args.port) {
      launchOptions.port = Number(args.port);
    }
    if (args.account) {
      launchOptions.account = args.account;
    }
    if (args.ticket) {
      launchOptions.ticket = args.ticket;
    }
    if (args.cwd) {
      launchOptions.cwd = args.cwd;
    }

    return automator.launch(launchOptions);
  }

  if (args.mode === 'connect') {
    if (!args.ws_endpoint) {
      throw new Error('--ws-endpoint is required in connect mode');
    }
    return automator.connect({ wsEndpoint: args.ws_endpoint });
  }

  throw new Error('--mode must be launch or connect');
}

function isoNow() {
  return new Date().toISOString();
}

function withActionTimeout(action, promiseFactory) {
  if (!action || typeof action.timeoutMs !== 'number' || action.timeoutMs <= 0) {
    return Promise.resolve().then(promiseFactory);
  }

  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`Action ${action.type} timed out after ${action.timeoutMs}ms`));
    }, action.timeoutMs);

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

async function withBestEffortTimeout(timeoutMs, promiseFactory) {
  return await new Promise((resolve) => {
    const timer = setTimeout(() => {
      resolve({ ok: false, error: `Timed out after ${timeoutMs}ms` });
    }, timeoutMs);

    Promise.resolve()
      .then(promiseFactory)
      .then((value) => {
        clearTimeout(timer);
        resolve({ ok: true, value });
      })
      .catch((error) => {
        clearTimeout(timer);
        resolve({ ok: false, error: error.message });
      });
  });
}

function simplifyPageStack(pages) {
  if (!Array.isArray(pages)) {
    return null;
  }

  return pages.map((page) => ({
    path: page.path,
    query: page.query,
  }));
}

async function collectFailureDiagnostics(miniProgram, artifacts) {
  if (!miniProgram) {
    return null;
  }

  const diagnostics = {};
  const currentPage = await withBestEffortTimeout(1000, async () => {
    const page = await miniProgram.currentPage();
    return simplifyPage(page);
  });
  diagnostics.currentPage = currentPage.ok ? currentPage.value : null;
  diagnostics.currentPageError = currentPage.ok ? null : currentPage.error;

  const pageStack = await withBestEffortTimeout(1000, async () => {
    const pages = await miniProgram.pageStack();
    return simplifyPageStack(pages);
  });
  diagnostics.pageStack = pageStack.ok ? pageStack.value : null;
  diagnostics.pageStackError = pageStack.ok ? null : pageStack.error;

  const snapshotPath = path.join(
    artifacts && artifacts.diagnosticsDir ? artifacts.diagnosticsDir : '/tmp',
    `wechat-automator-failure-${Date.now()}.json`
  );
  const snapshot = {
    currentPage: diagnostics.currentPage,
    pageStack: diagnostics.pageStack,
  };
  const snapshotResult = await withBestEffortTimeout(1000, async () => {
    const page = await getPage(miniProgram);
    snapshot.data = await page.data();
    fs.writeFileSync(snapshotPath, JSON.stringify(snapshot, null, 2));
    return snapshotPath;
  });
  diagnostics.snapshotPath = snapshotResult.ok ? snapshotResult.value : null;
  diagnostics.snapshotError = snapshotResult.ok ? null : snapshotResult.error;

  const screenshotPath = path.join(
    artifacts && artifacts.diagnosticsDir ? artifacts.diagnosticsDir : '/tmp',
    `wechat-automator-failure-${Date.now()}.png`
  );
  const screenshot = await withBestEffortTimeout(1500, async () => {
    await miniProgram.screenshot({ path: screenshotPath });
    return screenshotPath;
  });
  diagnostics.screenshotPath = screenshot.ok ? screenshot.value : null;
  diagnostics.screenshotError = screenshot.ok ? null : screenshot.error;

  return diagnostics;
}

function summarizeTelemetry(telemetry) {
  if (!telemetry) {
    return {
      consoleEventCount: 0,
      consoleTail: [],
      exceptionCount: 0,
      exceptionTail: [],
      requestEventCount: 0,
      requestTail: [],
    };
  }

  return {
    consoleEventCount: telemetry.consoleEvents.length,
    consoleTail: telemetry.consoleEvents.slice(-10),
    exceptionCount: telemetry.exceptions.length,
    exceptionTail: telemetry.exceptions.slice(-10),
    requestEventCount: telemetry.requestEvents.length,
    requestTail: telemetry.requestEvents.slice(-10),
  };
}

function writeTrace(artifacts, payload) {
  if (!artifacts) {
    return null;
  }
  fs.writeFileSync(artifacts.tracePath, JSON.stringify(payload, null, 2));
  return artifacts.tracePath;
}

async function attachTelemetry(miniProgram) {
  const consoleEvents = [];
  const exceptions = [];
  const requestEvents = [];
  const requestBindingName = `__codexAutomatorRequestEvent_${process.pid}_${Date.now()}`;
  const consoleListener = (event) => {
    consoleEvents.push(event);
    if (consoleEvents.length > 100) {
      consoleEvents.shift();
    }
  };
  const exceptionListener = (event) => {
    exceptions.push(event);
    if (exceptions.length > 50) {
      exceptions.shift();
    }
  };
  const requestListener = (event) => {
    const normalized = normalizeRequestEvent(event);
    if (!normalized) {
      return;
    }
    requestEvents.push(normalized);
    if (requestEvents.length > 100) {
      requestEvents.shift();
    }
  };

  await miniProgram.send('App.enableLog');
  EventEmitter.prototype.on.call(miniProgram, 'console', consoleListener);
  EventEmitter.prototype.on.call(miniProgram, 'exception', exceptionListener);
  await miniProgram.exposeFunction(requestBindingName, requestListener);
  await miniProgram.evaluate((bindingName) => {
    const root = typeof globalThis !== 'undefined' ? globalThis : Function('return this')();
    const stateKey = '__codexAutomatorRequestTelemetryState';
    const previousState = root[stateKey];
    if (previousState && typeof previousState.originalRequest === 'function') {
      wx.request = previousState.originalRequest;
    }

    const originalRequest = typeof wx !== 'undefined' && typeof wx.request === 'function'
      ? wx.request
      : null;
    if (typeof originalRequest !== 'function') {
      return {
        installed: false,
        reason: 'wx.request is not available',
      };
    }

    root[stateKey] = {
      bindingName,
      originalRequest,
      nextId: previousState && typeof previousState.nextId === 'number' ? previousState.nextId : 0,
    };

    const emit = (payload) => {
      try {
        const reporter = root[bindingName];
        if (typeof reporter === 'function') {
          reporter(payload);
        }
      } catch (error) {
        // Best effort telemetry only.
      }
    };

    wx.request = function codexInstrumentedRequest(options) {
      const safeOptions = options && typeof options === 'object' ? options : {};
      const state = root[stateKey];
      state.nextId += 1;
      const requestId = `request_${Date.now()}_${state.nextId}`;
      const startedAt = new Date().toISOString();
      const startedMs = Date.now();
      const method = typeof safeOptions.method === 'string' && safeOptions.method
        ? String(safeOptions.method).toUpperCase()
        : 'GET';
      const url = typeof safeOptions.url === 'string' ? safeOptions.url : '';
      const originalSuccess = safeOptions.success;
      const originalFail = safeOptions.fail;
      const originalComplete = safeOptions.complete;
      let finished = false;

      const finalize = (phase, payload) => {
        if (finished) {
          return;
        }
        finished = true;
        const endedAt = new Date().toISOString();
        const durationMs = Date.now() - startedMs;
        const statusCode = payload && typeof payload.statusCode === 'number' ? payload.statusCode : null;
        let ok = phase !== 'fail';
        if (ok && typeof statusCode === 'number') {
          ok = statusCode >= 200 && statusCode < 400;
        }
        emit({
          requestId,
          method,
          url,
          startAt: startedAt,
          endAt: endedAt,
          durationMs,
          statusCode,
          ok,
          error: phase === 'fail'
            ? (payload && (payload.errMsg || payload.errorMessage || String(payload))) || 'request failed'
            : null,
        });
      };

      const wrappedOptions = Object.assign({}, safeOptions, {
        success(result) {
          finalize('success', result);
          if (typeof originalSuccess === 'function') {
            return originalSuccess.apply(this, arguments);
          }
          return undefined;
        },
        fail(error) {
          finalize('fail', error);
          if (typeof originalFail === 'function') {
            return originalFail.apply(this, arguments);
          }
          return undefined;
        },
        complete(result) {
          if (!finished) {
            finalize(result && typeof result.statusCode === 'number' ? 'success' : 'fail', result);
          }
          if (typeof originalComplete === 'function') {
            return originalComplete.apply(this, arguments);
          }
          return undefined;
        },
      });

      try {
        return originalRequest.call(this, wrappedOptions);
      } catch (error) {
        finalize('fail', error);
        throw error;
      }
    };

    return {
      installed: true,
      bindingName,
    };
  }, requestBindingName);

  return {
    consoleEvents,
    exceptions,
    requestEvents,
    detach() {
      miniProgram.off('console', consoleListener);
      miniProgram.off('exception', exceptionListener);
      miniProgram.evaluate((bindingName) => {
        const root = typeof globalThis !== 'undefined' ? globalThis : Function('return this')();
        const stateKey = '__codexAutomatorRequestTelemetryState';
        const state = root[stateKey];
        if (state && typeof state.originalRequest === 'function') {
          wx.request = state.originalRequest;
        }
        if (state && state.bindingName === bindingName) {
          delete root[stateKey];
        }
        return true;
      }, requestBindingName).catch(() => {});
    },
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    printHelp();
    return;
  }

  const actions = readActions(args);
  const artifacts = resolveArtifacts(args);
  if (!Array.isArray(actions)) {
    throw new Error('Actions input must be a JSON array');
  }

  let miniProgram;
  let telemetry = null;
  let currentAction = null;
  let currentActionMeta = null;
  const runStartedAt = Date.now();
  const runStartedAtIso = isoNow();
  try {
    miniProgram = await openMiniProgram(args);
    telemetry = await attachTelemetry(miniProgram);
    const results = [];

    for (let index = 0; index < actions.length; index += 1) {
      const action = actions[index];
      currentAction = action;
      const actionStartedAt = Date.now();
      const actionStartedAtIso = isoNow();
      currentActionMeta = {
        index,
        type: action.type,
        startedAt: actionStartedAtIso,
      };
      const value = await withActionTimeout(action, () => runAction(miniProgram, action, { telemetry }));
      const actionEndedAt = Date.now();
      results.push({
        index,
        type: action.type,
        startedAt: actionStartedAtIso,
        endedAt: isoNow(),
        durationMs: actionEndedAt - actionStartedAt,
        timeoutMs: typeof action.timeoutMs === 'number' ? action.timeoutMs : null,
        value,
      });
      currentActionMeta = null;
    }

    process.stdout.write(
      `${JSON.stringify(
        {
          ok: true,
          mode: args.mode,
          startedAt: runStartedAtIso,
          endedAt: isoNow(),
          durationMs: Date.now() - runStartedAt,
          artifacts: artifacts ? { rootDir: artifacts.rootDir, tracePath: artifacts.tracePath } : null,
          ...summarizeTelemetry(telemetry),
          results,
        },
        null,
        2
      )}\n`
    );
    writeTrace(artifacts, {
      ok: true,
      mode: args.mode,
      startedAt: runStartedAtIso,
      endedAt: isoNow(),
      durationMs: Date.now() - runStartedAt,
      ...summarizeTelemetry(telemetry),
      results,
    });
  } catch (error) {
    const diagnostics = await collectFailureDiagnostics(miniProgram, artifacts);
    const tracePayload = {
      ok: false,
      mode: args.mode,
      startedAt: runStartedAtIso,
      endedAt: isoNow(),
      durationMs: Date.now() - runStartedAt,
      error: error.message,
      failedAction: currentAction,
      failedActionMeta: currentActionMeta,
      ...summarizeTelemetry(telemetry),
      diagnostics,
    };
    const tracePath = writeTrace(artifacts, tracePayload);
    process.stdout.write(
      `${JSON.stringify(
        {
          ...tracePayload,
          artifacts: artifacts ? { rootDir: artifacts.rootDir, tracePath } : null,
        },
        null,
        2
      )}\n`
    );
    process.exitCode = 1;
  } finally {
    if (telemetry) {
      telemetry.detach();
    }
    if (miniProgram && !args.keepOpen) {
      try {
        if (args.mode === 'connect') {
          miniProgram.disconnect();
        } else {
          await miniProgram.close();
        }
      } catch (closeError) {
        // Ignore close failures so the original result remains visible.
      }
    }
  }
}

main();
