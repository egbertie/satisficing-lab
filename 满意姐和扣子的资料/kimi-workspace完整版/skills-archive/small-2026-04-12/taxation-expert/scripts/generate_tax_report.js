/**
 * 税务咨询报告Word文档生成脚本
 * 用法: node generate_tax_report.js <输出路径> <JSON数据>
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
        LevelFormat, Header, Footer, PageNumber, convertInchesToTwip } = require('docx');
const fs = require('fs');

const C = {
  primary: '1F4E79',
  secondary: '2E75B6',
  headerBg: 'D6DCE4',
  border: 'ADB9CA',
  accent: 'E7E6E6',
};

const border = { style: BorderStyle.SINGLE, size: 1, color: C.border };
const borders = { top: border, bottom: border, left: border, right: border };

const styles = {
  default: { document: { run: { font: '宋体', size: 24 } } },
  paragraphStyles: [
    { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', quickFormat: true,
      run: { size: 36, bold: true, font: '黑体', color: C.primary },
      paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 } },
    { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', quickFormat: true,
      run: { size: 32, bold: true, font: '黑体', color: C.secondary },
      paragraph: { spacing: { before: 300, after: 180 }, outlineLevel: 1 } },
  ]
};

const numbering = {
  config: [{
    reference: 'bullets',
    levels: [{ level: 0, format: LevelFormat.BULLET, text: '\u25CF', alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
  }]
};

// 检测是否为分点标记行
function isListItem(line) {
  // 匹配：1. 、1、、(1)、①、-、*、•、· 等标记
  return /^\s*(\d+[\.、]|[\(（]\d+[\)）]|[①②③④⑤⑥⑦⑧⑨⑩]|[\-\*•·]|[一二三四五六七八九十]+[、\.])\s*/.test(line);
}

// 检测是否为嵌套分点（二级分点）
function isNestedListItem(line) {
  return /^\s*[\(（][\d一二三四五六七八九十]+[\)）]\s*/.test(line) || 
         /^\s*[\-\*•·]\s+/.test(line);
}

// 获取分点标记后的缩进级别
function getIndentLevel(line) {
  if (isNestedListItem(line)) return 2;
  if (isListItem(line)) return 1;
  return 0;
}

// 检测是否为Markdown表格行（| ... | ... |）
function isTableLine(line) {
  const trimmed = line.trim();
  return trimmed.startsWith('|') && trimmed.endsWith('|');
}

// 检测是否为表格分隔行（|---|---|）
function isTableSeparator(line) {
  const trimmed = line.trim();
  if (!isTableLine(line)) return false;
  // 去掉首尾 | 后，检查是否全是 -、:、空格
  const inner = trimmed.slice(1, -1).trim();
  return /^[\|\s\:\-]+$/.test(inner);
}

// 解析Markdown表格为结构化数据
function parseMarkdownTable(lines, startIdx) {
  const headers = [];
  const rows = [];
  let i = startIdx;
  
  // 解析表头
  if (i < lines.length && isTableLine(lines[i])) {
    const headerCells = lines[i].trim().slice(1, -1).split('|').map(c => c.trim());
    headers.push(...headerCells);
    i++;
  }
  
  // 跳过分隔行
  if (i < lines.length && isTableSeparator(lines[i])) {
    i++;
  }
  
  // 解析数据行
  while (i < lines.length && isTableLine(lines[i]) && !isTableSeparator(lines[i])) {
    const cells = lines[i].trim().slice(1, -1).split('|').map(c => c.trim());
    rows.push(cells);
    i++;
  }
  
  return { headers, rows, nextIdx: i };
}

// 将Markdown表格转换为Word表格元素
function createTableFromMarkdown(headers, rows) {
  const colCount = headers.length || (rows[0] && rows[0].length) || 1;
  // 计算各列宽度，总宽9360
  const colWidth = Math.floor(9360 / colCount);
  const colWidths = Array(colCount).fill(colWidth);
  
  const tableRows = [];
  
  // 表头行
  if (headers.length > 0) {
    tableRows.push(new TableRow({
      tableHeader: true,
      children: headers.map(h => new TableCell({
        borders,
        width: { size: colWidth, type: WidthType.DXA },
        shading: { fill: C.headerBg, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 100, right: 100 },
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { line: 300 },
          children: [new TextRun({ text: h, font: '宋体', size: 21, bold: true, color: '333333' })]
        })]
      }))
    }));
  }
  
  // 数据行
  rows.forEach(row => {
    tableRows.push(new TableRow({
      children: row.map((cell, ci) => new TableCell({
        borders,
        width: { size: colWidth, type: WidthType.DXA },
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({
          alignment: ci === 0 ? AlignmentType.CENTER : AlignmentType.LEFT,
          spacing: { line: 280 },
          children: [new TextRun({ text: cell, font: '宋体', size: 21, color: '333333' })]
        })]
      }))
    }));
  });
  
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: tableRows
  });
}

// 智能分段：将包含分点的文本拆分为多个段落，并识别Markdown表格
function parseContentToParagraphs(text) {
  if (!text) return [];

  // 规范化换行符：将字面的 \n（两个字符：反斜杠+n）统一替换为真正的换行符
  // 因为通过命令行传递JSON时，AI可能传入字面\n而非真正的换行
  let normalized = text.replace(/\\n/g, '\n');

  // 按换行符分割
  const lines = normalized.split(/\n/);
  const paragraphs = [];
  let currentBlock = [];
  
  let i = 0;
  while (i < lines.length) {
    const line = lines[i].trim();
    
    // 空行跳过
    if (!line) { i++; continue; }
    
    // 检测Markdown表格
    if (isTableLine(line) && !isTableSeparator(line)) {
      // 先保存之前的累积内容
      if (currentBlock.length > 0) {
        paragraphs.push({ text: currentBlock.join(''), indent: 0 });
        currentBlock = [];
      }
      // 解析整个表格
      const table = parseMarkdownTable(lines, i);
      paragraphs.push({ type: 'table', headers: table.headers, rows: table.rows });
      i = table.nextIdx;
      continue;
    }
    
    const indentLevel = getIndentLevel(line);
    
    if (indentLevel > 0) {
      // 如果是分点行，先保存之前的累积内容
      if (currentBlock.length > 0) {
        paragraphs.push({ text: currentBlock.join(''), indent: 0 });
        currentBlock = [];
      }
      // 添加分点段落
      paragraphs.push({ text: line, indent: indentLevel });
    } else {
      // 普通文本行，累积到当前块
      currentBlock.push(line);
    }
    i++;
  }
  
  // 处理最后累积的内容
  if (currentBlock.length > 0) {
    paragraphs.push({ text: currentBlock.join(''), indent: 0 });
  }
  
  return paragraphs;
}

// 创建带格式的段落
function createFormattedParagraph(text, opts = {}) {
  const indentLevel = opts.indent || 0;
  const baseIndent = 360; // 基础缩进值
  
  return new Paragraph({
    spacing: { line: 360, after: 120, before: indentLevel > 0 ? 60 : 0 },
    alignment: opts.align || AlignmentType.JUSTIFIED,
    indent: indentLevel > 0 ? { left: baseIndent * indentLevel } : undefined,
    children: [new TextRun({ 
      text, 
      font: '宋体', 
      size: 24, 
      bold: opts.bold, 
      color: opts.color || '333333' 
    })]
  });
}

function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, font: '黑体', size: 36, bold: true, color: C.primary })] });
}

function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, font: '黑体', size: 32, bold: true, color: C.secondary })] });
}

// 普通段落（支持自动分点换行和Markdown表格）
function p(text, opts = {}) {
  const paragraphs = parseContentToParagraphs(text);
  return paragraphs.map(para => {
    if (para.type === 'table') {
      return createTableFromMarkdown(para.headers, para.rows);
    }
    return createFormattedParagraph(para.text, { ...opts, indent: para.indent });
  });
}

// 单一段落（不换行）
function pSingle(text, opts = {}) {
  return createFormattedParagraph(text, opts);
}

function quote(text) {
  const paragraphs = parseContentToParagraphs(text);
  return paragraphs.map(para => {
    if (para.type === 'table') {
      return createTableFromMarkdown(para.headers, para.rows);
    }
    return new Paragraph({
      spacing: { line: 320, after: 120, before: para.indent > 0 ? 60 : 0 },
      indent: { left: 720 + (para.indent > 0 ? 360 * para.indent : 0) },
      shading: { fill: C.accent, type: ShadingType.CLEAR },
      children: [new TextRun({ text: para.text, font: '楷体', size: 24, color: '444444' })]
    });
  });
}

function refTable(refs) {
  const colWidths = [600, 3800, 2960, 2000];
  const headerRow = new TableRow({
    tableHeader: true,
    children: ['序号', '文件名称', '文号', '发布日期'].map((h, i) =>
      new TableCell({ borders, width: { size: colWidths[i], type: WidthType.DXA },
        shading: { fill: C.headerBg, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 120, right: 120 },
        children: [new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: h, font: '宋体', size: 22, bold: true })] })] })
    )
  });
  const dataRows = refs.map((r, idx) => new TableRow({
    children: [String(idx + 1), r.name || '', r.code || '', r.date || ''].map((v, i) =>
      new TableCell({ borders, width: { size: colWidths[i], type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({ alignment: i === 0 ? AlignmentType.CENTER : AlignmentType.LEFT,
          children: [new TextRun({ text: v, font: '宋体', size: 22 })] })] })
    )
  }));
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: colWidths, rows: [headerRow, ...dataRows] });
}

function disclaimer() {
  return new Paragraph({
    spacing: { line: 360 },
    shading: { fill: 'FFF3CD', type: ShadingType.CLEAR },
    border: { left: { style: BorderStyle.SINGLE, size: 24, color: 'FFC107' } },
    children: [
      new TextRun({ text: '【免责声明】', font: '宋体', size: 24, bold: true, color: '856404' }),
      new TextRun({ text: ' 本回答仅为税务政策解读与参考意见，不构成正式税务法律意见。具体执行以主管税务机关最终口径为准。', font: '宋体', size: 24, color: '856404' })
    ]
  });
}

async function generate(outputPath, data) {
  const children = [];

  // 标题
  children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 480 },
    children: [new TextRun({ text: data.title || '税务咨询意见书', font: '黑体', size: 44, bold: true, color: C.primary })] }));
  children.push(new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: C.secondary } }, spacing: { after: 360 } }));

  // 咨询问题
  if (data.question) {
    children.push(h2('一、咨询问题'));
    children.push(new Paragraph({
      spacing: { line: 360, after: 240 },
      shading: { fill: 'F0F4F8', type: ShadingType.CLEAR },
      border: { left: { style: BorderStyle.SINGLE, size: 24, color: C.secondary } },
      indent: { left: 240 },
      children: [new TextRun({ text: data.question, font: '宋体', size: 24, color: '333333' })]
    }));
  }

  // 核心结论
  children.push(h2(data.question ? '二、核心结论' : '一、核心结论'));
  children.push(...quote(data.conclusion || ''));

  // 政策依据
  if (data.policies && data.policies.length) {
    children.push(h2(data.question ? '三、政策依据' : '二、政策依据'));
    data.policies.forEach(pol => {
      children.push(new Paragraph({ spacing: { line: 320, after: 60 },
        children: [new TextRun({ text: `【${pol.name}】`, font: '宋体', size: 24, bold: true, color: C.primary })] }));
      children.push(pSingle(`条款：${pol.clause}`, { bold: true }));
      // 政策内容支持分点换行
      children.push(...p(`内容：${pol.content}`));
      children.push(pSingle(`来源：${pol.source}`, { color: '666666' }));
    });
  }

  // 引用出处
  if (data.references && data.references.length) {
    children.push(h2(data.question ? '四、引用出处' : '三、引用出处'));
    children.push(refTable(data.references));
  }

  // 补充说明
  if (data.notes) {
    children.push(h2(data.question ? '五、补充说明' : '四、补充说明'));
    children.push(...p(data.notes));
  }

  // 免责声明
  children.push(h2(data.question ? '六、免责声明' : '五、免责声明'));
  children.push(disclaimer());

  const doc = new Document({
    styles,
    numbering,
    sections: [{
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1800, right: 1440, bottom: 1800, left: 1440 } } },
      headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.secondary } },
        children: [new TextRun({ text: '税务咨询意见', font: '宋体', size: 18, color: '666666' })] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: '第 ', font: '宋体', size: 18, color: '666666' }),
                   new TextRun({ children: [PageNumber.CURRENT], font: '宋体', size: 18, color: '666666' }),
                   new TextRun({ text: ' 页', font: '宋体', size: 18, color: '666666' })] })] }) },
      children
    }]
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log(`报告已生成: ${outputPath}`);
}

// 主程序
const args = process.argv.slice(2);
if (args.length >= 1) {
  const outputPath = args[0];
  const dataStr = args.length > 1 ? args[1] : '{}';
  try {
    const data = JSON.parse(dataStr);
    generate(outputPath, data).catch(console.error);
  } catch (e) {
    console.error('JSON解析错误:', e.message);
  }
} else {
  console.log('用法: node generate_tax_report.js <输出路径> <JSON数据>');
}
