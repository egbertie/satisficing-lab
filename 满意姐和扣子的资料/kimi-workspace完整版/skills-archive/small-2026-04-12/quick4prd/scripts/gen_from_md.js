/**
 * gen_from_md.js
 * 统一运营系统文档生成器 v2
 *
 * 直接解析 .md 源文件 → 生成 .docx 快照，不依赖 hardcode build 函数。
 * 版本号从源文件「文档版本」字段读取，与 .md 快照保持严格一致。
 *
 * 用法：
 *   DOC_DIR=/path/to/doc node gen_from_md.js --doc sim,obu
 *   DOC_DIR=/path/to/doc node gen_from_md.js          # 生成全部
 */

'use strict';

const docx = require('docx');
const fs   = require('fs');
const path = require('path');

const {
  Document, Paragraph, TextRun, Table, TableCell, TableRow,
  WidthType, AlignmentType, ShadingType, Packer
} = docx;

// ── 排版常量 ──────────────────────────────────────────────
const SONGTI      = 'SimSun';
const BODY_SIZE   = 21;   // 10.5pt
const H1_SIZE     = 44;   // 22pt
const H2_SIZE     = 32;   // 16pt
const H3_SIZE     = 28;   // 14pt
const H4_SIZE     = 25;   // 12.5pt
const LINE_SPACE  = { line: 360, lineRule: 'auto' };
const HEADER_CLR  = 'D9E1F2';
const DXA_TOTAL   = 9072; // A4 可用宽度（twip）

// ── 基础段落构建函数 ──────────────────────────────────────
function mkBody(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({
      text: String(text),
      font: SONGTI,
      size: BODY_SIZE,
      bold: opts.bold || false,
    })],
    spacing: { ...LINE_SPACE, before: opts.before || 0, after: opts.after || 0 },
    alignment: opts.align || AlignmentType.LEFT,
    indent: opts.indent ? { left: opts.indent } : undefined,
    bullet: opts.bullet ? { level: 0 } : undefined,
  });
}

function mkH(text, level) {
  const sizeMap = { 1: H1_SIZE, 2: H2_SIZE, 3: H3_SIZE, 4: H4_SIZE };
  const spaceMap = {
    1: { before: 300, after: 200 },
    2: { before: 300, after: 150 },
    3: { before: 200, after: 100 },
    4: { before: 160, after:  80 },
  };
  return new Paragraph({
    children: [new TextRun({ text, font: SONGTI, size: sizeMap[level] || BODY_SIZE, bold: true })],
    spacing: { ...LINE_SPACE, ...spaceMap[level] },
    alignment: level === 1 ? AlignmentType.CENTER : AlignmentType.LEFT,
  });
}

function mkBlank() {
  return new Paragraph({ children: [new TextRun({ text: '' })], spacing: { line: 200 } });
}

function mkCell(text, isHeader = false) {
  return new TableCell({
    children: [new Paragraph({
      children: [new TextRun({ text: String(text), font: SONGTI, size: BODY_SIZE, bold: isHeader })],
      spacing: LINE_SPACE,
      alignment: AlignmentType.LEFT,
    })],
    shading: isHeader
      ? { fill: HEADER_CLR, type: ShadingType.CLEAR }
      : { fill: 'FFFFFF',   type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
  });
}

function mkTable(headers, rows) {
  const colCount = headers.length;
  const colW = Math.floor(DXA_TOTAL / colCount);
  const colWidths = headers.map((_, i) =>
    i < colCount - 1 ? colW : DXA_TOTAL - colW * (colCount - 1)
  );
  const headerRow = new TableRow({
    children: headers.map(h => mkCell(h, true)),
    tableHeader: true,
  });
  const dataRows = rows.map(r =>
    new TableRow({ children: r.map(c => mkCell(c, false)) })
  );
  return new Table({
    rows: [headerRow, ...dataRows],
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: colWidths,
  });
}

// ── Markdown 解析器 ───────────────────────────────────────
/**
 * 将 Markdown 文本解析为 docx 段落/表格元素数组。
 *
 * 支持：
 *  - # ~ #### 标题
 *  - | 表格（含 |:---:| 分隔行）
 *  - - / * 无序列表
 *  - --- 分割线（跳过）
 *  - 空行
 *  - 普通段落
 */
function parseMd(mdText) {
  const elements = [];
  const lines = mdText.split(/\r?\n/);
  let i = 0;

  while (i < lines.length) {
    const raw = lines[i];
    const line = raw.trimEnd();

    // 1. 标题
    const hMatch = line.match(/^(#{1,4})\s+(.+)/);
    if (hMatch) {
      elements.push(mkH(hMatch[2].trim(), hMatch[1].length));
      i++;
      continue;
    }

    // 2. 表格：检测是否是表格起始行（含 | 且下一行是 |:---| 分隔行）
    if (line.startsWith('|') && i + 1 < lines.length && lines[i + 1].match(/^\|[\s\-:|]+\|/)) {
      // 收集所有连续的表格行
      const tableLines = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        tableLines.push(lines[i].trim());
        i++;
      }
      // 解析表格
      const parsed = parseTable(tableLines);
      if (parsed) elements.push(parsed);
      continue;
    }

    // 3. 分割线
    if (/^---+$/.test(line.trim())) {
      i++;
      continue;
    }

    // 4. 无序列表项
    const liMatch = line.match(/^(\s*)[*\-+]\s+(.+)/);
    if (liMatch) {
      const indent = liMatch[1].length > 0 ? 720 : 360;
      elements.push(mkBody('• ' + liMatch[2].trim(), { indent }));
      i++;
      continue;
    }

    // 5. 空行
    if (line.trim() === '') {
      elements.push(mkBlank());
      i++;
      continue;
    }

    // 6. 普通段落（去除粗体/斜体 markdown 标记，保留纯文本）
    const plain = line.trim()
      .replace(/\*\*(.+?)\*\*/g, '$1')  // **bold**
      .replace(/\*(.+?)\*/g, '$1')       // *italic*
      .replace(/`(.+?)`/g, '$1');        // `code`
    if (plain) {
      elements.push(mkBody(plain));
    }
    i++;
  }

  return elements;
}

/**
 * 解析 Markdown 表格行数组 → docx Table
 * tableLines: ['| A | B |', '|---|---|', '| 1 | 2 |', ...]
 */
function parseTable(tableLines) {
  // 过滤掉分隔行（|:---:|）
  const dataLines = tableLines.filter(l => !l.match(/^\|[\s\-:|]+\|$/));
  if (dataLines.length < 1) return null;

  const parseRow = (line) =>
    line.split('|')
      .slice(1, -1)           // 去掉首尾空字符串
      .map(c => c.trim()
        .replace(/\*\*(.+?)\*\*/g, '$1')
        .replace(/\*(.+?)\*/g, '$1')
        .replace(/`(.+?)`/g, '$1')
      );

  const headers = parseRow(dataLines[0]);
  const rows    = dataLines.slice(1).map(parseRow);

  return mkTable(headers, rows);
}

// ── 版本号读取 ────────────────────────────────────────────
function readVersionFromMd(mdPath) {
  if (!fs.existsSync(mdPath)) return null;
  const content = fs.readFileSync(mdPath, 'utf8');
  const m = content.match(/\|\s*文档版本\s*\|\s*(v[\d.]+)\s*\|/i);
  return m ? m[1] : null;
}

// ── 旧快照归档 ────────────────────────────────────────────
function archiveOldSnapshots(outDir, baseName) {
  const backupDir = path.join(outDir, 'backup');
  if (!fs.existsSync(backupDir)) fs.mkdirSync(backupDir, { recursive: true });

  const re = new RegExp(
    `^${baseName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}_v[\\d.]+\\.(docx|md)$`
  );
  fs.readdirSync(outDir).forEach(f => {
    if (re.test(f)) {
      fs.renameSync(path.join(outDir, f), path.join(backupDir, f));
      console.log(`  → 已归档旧版本：${f}`);
    }
  });
}

// ── 核心：生成单个文档 ────────────────────────────────────
async function generateDoc(outDir, baseName) {
  const mdSrcPath = path.join(outDir, `${baseName}.md`);

  if (!fs.existsSync(mdSrcPath)) {
    console.error(`✗ 找不到源文件：${mdSrcPath}`);
    return;
  }

  const ver = readVersionFromMd(mdSrcPath) || 'v0.1';
  console.log(`  → 版本号：${ver}`);

  // 归档旧快照
  archiveOldSnapshots(outDir, baseName);

  const docxName = `${baseName}_${ver}.docx`;
  const mdName   = `${baseName}_${ver}.md`;

  // 解析 md → docx 元素
  const mdText   = fs.readFileSync(mdSrcPath, 'utf8');
  const elements = parseMd(mdText);

  // 构建 Document
  const doc = new Document({
    sections: [{
      properties: {
        page: {
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
          size:   { width: 11906, height: 16838 },
        },
      },
      children: elements,
    }],
  });

  // 写 docx
  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(path.join(outDir, docxName), buf);
  console.log(`✓ ${docxName}`);

  // 复制 .md 快照
  fs.copyFileSync(mdSrcPath, path.join(outDir, mdName));
  console.log(`✓ ${mdName}`);
}

// ── 已注册文档映射表 ──────────────────────────────────────
// 只需维护 base（文件名不含后缀），不再需要 build 函数
const ALL_DOCS = {
  'vehicle':      '统一运营系统-车辆监控管理功能设计',
  'homepage':     '统一运营系统-首页概览功能设计',
  'sim':          '统一运营系统-SIM卡信息管理功能设计',
  'obu':          '统一运营系统-OBU信息管理功能设计',
  'vehicle-info': '统一运营系统-车辆信息管理功能设计',
  'car-type':     '统一运营系统-车型字典管理功能设计',
  'system':       '统一运营系统-系统管理功能设计',
};

// ── 入口 ──────────────────────────────────────────────────
async function main() {
  const outDir = process.env.DOC_DIR
    || path.join(process.cwd(), 'tongyiyunying', 'doc');

  // 解析 --doc 参数
  const args = process.argv.slice(2);
  const requestedKeys = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--doc' && args[i + 1]) {
      args[i + 1].split(',').forEach(k => requestedKeys.push(k.trim()));
      i++;
    }
  }

  let targets = [];
  if (requestedKeys.length > 0) {
    for (const key of requestedKeys) {
      if (ALL_DOCS[key]) {
        targets.push({ key, base: ALL_DOCS[key] });
      } else {
        console.error(`✗ 未知文档 key: "${key}"，可用 key：${Object.keys(ALL_DOCS).join('、')}`);
        process.exit(1);
      }
    }
  } else {
    targets = Object.entries(ALL_DOCS).map(([key, base]) => ({ key, base }));
  }

  console.log(`\n📄 本次将生成 ${targets.length} 个文档快照：`);
  targets.forEach(t => console.log(`   - ${t.base}`));
  console.log('');

  for (const t of targets) {
    await generateDoc(outDir, t.base);
  }

  console.log('\n✅ 完成');
}

main().catch(console.error);
