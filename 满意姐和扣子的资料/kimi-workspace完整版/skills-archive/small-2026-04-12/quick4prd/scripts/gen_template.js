const docx = require('docx');
const fs = require('fs');
const path = require('path');

const {
  Document, Paragraph, TextRun, Table, TableCell, TableRow,
  WidthType, AlignmentType, ShadingType
} = docx;

const SONGTI = 'SimSun';
const BODY_SIZE = 21;
const H1_SIZE = 44;
const H2_SIZE = 32;
const H3_SIZE = 28;
const H4_SIZE = 25;
const LINE_SPACING = { line: 360, lineRule: 'auto' };
const HEADER_COLOR = 'D9E1F2'; // 淡蓝色表头

function body(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text: String(text), font: SONGTI, size: BODY_SIZE, bold: opts.bold || false, italics: opts.italic || false })],
    spacing: { ...LINE_SPACING, before: opts.before || 0, after: opts.after || 0 },
    alignment: opts.align || AlignmentType.LEFT,
    indent: opts.indent ? { left: opts.indent } : undefined
  });
}

function h1(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: SONGTI, size: H1_SIZE, bold: true })],
    spacing: { ...LINE_SPACING, before: 300, after: 200 },
    alignment: AlignmentType.CENTER
  });
}
function h2(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: SONGTI, size: H2_SIZE, bold: true })],
    spacing: { ...LINE_SPACING, before: 300, after: 150 }
  });
}
function h3(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: SONGTI, size: H3_SIZE, bold: true })],
    spacing: { ...LINE_SPACING, before: 200, after: 100 }
  });
}
function h4(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: SONGTI, size: H4_SIZE, bold: true })],
    spacing: { ...LINE_SPACING, before: 160, after: 80 }
  });
}
function blank() {
  return new Paragraph({ children: [new TextRun({ text: '' })], spacing: { line: 200 } });
}

function cell(text, isHeader = false) {
  return new TableCell({
    children: [new Paragraph({
      children: [new TextRun({ text: String(text), font: SONGTI, size: BODY_SIZE, bold: isHeader })],
      spacing: { ...LINE_SPACING },
      alignment: AlignmentType.LEFT
    })],
    shading: isHeader
      ? { fill: HEADER_COLOR, type: ShadingType.CLEAR }
      : { fill: 'FFFFFF', type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 }
  });
}

function makeTable(headers, rows, colWidths) {
  const DXA_TOTAL = 9072;
  const headerRow = new TableRow({
    children: headers.map(h => cell(h, true)),
    tableHeader: true
  });
  const dataRows = rows.map(r => new TableRow({
    children: r.map(c => cell(c, false))
  }));
  return new Table({
    rows: [headerRow, ...dataRows],
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: colWidths.map(p => Math.round(DXA_TOTAL * p / 100))
  });
}

function buildTemplate() {
  const c = [];

  c.push(h1('统一运营系统 · xxxxx功能设计'));

  // 文档信息
  c.push(h2('文档信息'));
  c.push(makeTable(
    ['项目', '内容'],
    [
      ['文档编号', '【替换】PRD-XXX-2026-001'],
      ['文档版本', 'V1.0'],
      ['产品名称', '【替换】xxxxx'],
      ['所属系统', '统一运营系统'],
      ['编制日期', '【替换】YYYY-MM-DD'],
      ['编制人员', '【替换】姓名']
    ],
    [35, 65]
  ));
  c.push(blank());

  c.push(h3('修订记录'));
  c.push(makeTable(
    ['版本', '修订日期', '修订说明', '修订人'],
    [['V1.0', '【替换】YYYY-MM-DD', '初稿创建', '【替换】姓名']],
    [10, 20, 55, 15]
  ));
  c.push(blank());

  // 使用说明
  c.push(body('文档使用说明', { bold: true }));
  c.push(body('【替换】标记的内容：使用时替换为实际业务内容', { indent: 360 }));
  c.push(body('【删除】标记的内容：仅为填写说明，完成后删除', { indent: 360 }));
  c.push(body('本模板供 AI 开发智能体（Copilot、OpenCode 等）读取，请保持结构完整', { indent: 360 }));
  c.push(blank());

  // 一
  c.push(h2('一、功能角色矩阵说明'));
  c.push(h3('1.1 功能描述'));
  c.push(body('功能名称：【替换】xxxxx'));
  c.push(body('所属模块：【替换】xxxxx管理'));
  c.push(body('功能描述：【替换】简要描述该功能的定位和核心用途，一两句话即可。'));
  c.push(blank());

  c.push(h3('1.2 角色权限总览'));
  c.push(body('【删除】列举访问此功能的角色，以及各角色的功能权限和数据权限范围。', { italic: true }));
  c.push(makeTable(
    ['角色', '功能权限', '数据权限'],
    [
      ['系统超级管理员', '查看列表、查看详情、新增、修改、查询、删除、导入、导出', '全量数据'],
      ['平台运营管理员', '查看列表、查看详情、新增、修改、查询、删除、导入、导出', '全量数据'],
      ['机构管理员', '无权限', '无权限'],
      ['访客', '无权限', '无权限']
    ],
    [25, 50, 25]
  ));
  c.push(blank());

  c.push(h3('1.3 功能角色矩阵'));
  c.push(body('【删除】每个功能操作是否有权限用"是/否"标注，可按实际功能增减行。', { italic: true }));
  c.push(makeTable(
    ['功能点', '系统超级管理员', '平台运营管理员', '机构管理员', '访客'],
    [
      ['查看列表', '是', '是', '否', '否'],
      ['查看详情', '是', '是', '否', '否'],
      ['新增', '是', '是', '否', '否'],
      ['修改', '是', '是', '否', '否'],
      ['删除', '是', '是', '否', '否'],
      ['查询', '是', '是', '否', '否'],
      ['导入', '是', '是', '否', '否'],
      ['导出', '是', '是', '否', '否']
    ],
    [30, 17.5, 17.5, 17.5, 17.5]
  ));
  c.push(blank());

  // 二
  c.push(h2('二、模块路径'));
  c.push(body('【删除】描述用户从系统首页进入本功能页面的完整菜单路径，确保开发将页面挂载到正确导航节点。', { italic: true }));
  c.push(body('平台首页 → 【替换】一级菜单 → 【替换】二级菜单 → 【替换】本功能页面'));
  c.push(blank());

  // 三
  c.push(h2('三、页面布局'));
  c.push(h3('3.1 页面标题区'));
  c.push(body('显示"【替换】功能名称"标题。'));
  c.push(blank());

  c.push(h3('3.2 信息查询区'));
  c.push(body('【删除】列出所有查询字段，填写组件类型、初始状态、约束规则；搜索/重置按钮放在最后。', { italic: true }));
  c.push(makeTable(
    ['信息字段', '组件类型', '位置', '初始状态', '约束规则'],
    [
      ['【替换】字段1', '输入框', '居左', '提示"请输入【替换】字段1"', '【替换】精确/模糊查询；最大xx字符'],
      ['【替换】字段2', '下拉框', '居左', '提示"请选择【替换】字段2"', '精确查询；数据源参见第十二章数据字典'],
      ['查询', '深色按钮', '居右', '—', '点击触发筛选'],
      ['重置', '浅色按钮', '居右', '—', '点击清空所有筛选条件，恢复初始状态']
    ],
    [16, 14, 8, 22, 40]
  ));
  c.push(blank());

  c.push(h3('3.3 列表操作区'));
  c.push(body('【删除】列出列表上方工具栏的按钮，填写初始状态和约束规则。', { italic: true }));
  c.push(makeTable(
    ['操作项', '组件类型', '初始状态', '约束规则', '显示位置'],
    [
      ['新增', '深色按钮', '可用', '始终可用', '居右'],
      ['删除', '深色按钮', '灰化', '勾选数据后激活；支持批量删除', '居右'],
      ['导入', '深色按钮', '可用', '始终可用', '居右'],
      ['导出', '浅色按钮', '可用', '始终可用；未勾选时导出全量', '居右'],
      ['下载模板', '浅色按钮', '可用', '始终可用', '居右']
    ],
    [14, 14, 14, 42, 16]
  ));
  c.push(blank());

  c.push(h3('3.4 列表展示区'));
  c.push(body('【删除】列出所有列表字段，填写类型、是否必选、约束规则和示例；操作列放最后。', { italic: true }));
  c.push(body('表头字体加粗，列宽适配字段内容，操作列固定宽度，确保所有按钮正常显示。'));
  c.push(makeTable(
    ['字段', '类型', '是否必选', '约束规则', '举例或枚举'],
    [
      ['序号', '数字', '是', '正整数，从1开始依次递增', '1、2、3'],
      ['【替换】字段1', '文本', '是', '【替换】约束规则', '【替换】示例值'],
      ['【替换】字段2', '文本', '是', '【替换】约束规则', '【替换】示例值'],
      ['添加时间', '文本', '是', '格式 YYYY-MM-DD HH:mm:ss', '2026-01-01 12:00:00'],
      ['操作列', '按钮组', '是', '查看：始终可用；修改/删除：按业务规则', '查看、修改、删除']
    ],
    [16, 10, 12, 38, 24]
  ));
  c.push(blank());

  c.push(h3('3.5 分页控件区'));
  c.push(makeTable(
    ['控件', '组件类型', '初始状态', '约束规则'],
    [
      ['总条数', '文本', '共0条记录', '支持从0开始的所有非负整数'],
      ['当前页数', '文本', '第1/1页', '格式："第"+当前页码+"/"+总页数+"页"'],
      ['向前翻页', '浅色按钮', '左箭头', '首页时禁用'],
      ['页码按钮', '浅色按钮组', '从1开始，当前页高亮', '页码范围不超过总页数'],
      ['向后翻页', '浅色按钮', '右箭头', '末页时禁用'],
      ['每页条目数', '下拉框', '10条/页', '支持10/20/50条'],
      ['跳转至页码', '输入框', '1', '"跳至"+输入框+"页"，输入为不超过总页数的正整数']
    ],
    [15, 20, 20, 45]
  ));
  c.push(blank());

  // 四
  c.push(h2('四、交互说明'));
  c.push(body('【删除】列出本页面所有交互操作，填写可用性条件、正向交互结果和异常交互处理。', { italic: true }));
  c.push(makeTable(
    ['交互类型', '交互可用性', '正向交互', '异常交互'],
    [
      ['新增', '始终可用', '点击"新增"按钮，打开"新增【替换】"弹窗', '无'],
      ['查询', '始终可用', '点击"查询"触发筛选，展示符合条件的数据', '【替换】字段格式错误时输入框变红，下方红字提示错误信息；修正后自动消失'],
      ['重置', '始终可用', '清空所有筛选条件，恢复初始查询状态', '无'],
      ['查看', '始终可用', '点击操作列"查看"按钮，展示查看弹窗，所有字段只读', '无'],
      ['修改', '【替换】未被引用时可用', '打开"编辑【替换】"弹窗，反显当前数据，支持编辑', '已被引用时按钮灰化不可点击'],
      ['删除', '【替换】未被引用时可用', '弹出确认弹窗"是否确认删除？"；确认后执行删除，自动刷新列表', '已被引用时按钮灰化不可点击'],
      ['导入', '始终可用', '打开"批量导入"弹窗，支持上传Excel文件完成批量录入', '必填项不完整时提示"导入完成，失败X条，成功Y条，请检查后重新导入"'],
      ['下载模板', '始终可用', '触发本地文件管理弹窗，下载批量导入模板.xlsx', '模板关联数据获取失败时弹出提示，同时停止下载'],
      ['导出', '始终可用', '勾选数据时导出勾选行；未勾选时导出全量数据，下载Excel文件', '无数据时Toast提示"暂无数据可导出"']
    ],
    [16, 22, 32, 30]
  ));
  c.push(blank());

  // 五
  c.push(h2('五、字段输入规范'));
  c.push(body('【删除】列出新增/修改时所有字段的输入规范，填写类型、必填、约束规则和举例。', { italic: true }));
  c.push(makeTable(
    ['字段', '类型', '是否必填', '约束规则', '举例或枚举'],
    [
      ['【替换】字段1', '文本', '是', '【替换】约束规则，如：支持1-20个汉字，无特殊符号', '【替换】示例值'],
      ['【替换】字段2', '文本', '是', '枚举：【替换】选项A、选项B，二选一', '【替换】选项A、选项B'],
      ['【替换】字段3（只读）', '文本', '—', '系统自动生成，不可手动输入', '【替换】示例值']
    ],
    [16, 10, 12, 38, 24]
  ));
  c.push(blank());

  // 六
  c.push(h2('六、操作输出规则'));
  c.push(body('【删除】列出所有操作触发后的输出结果，区分正向输出和异常场景。', { italic: true }));
  c.push(makeTable(
    ['操作类型', '触发操作', '正向输出', '异常场景', '异常处理'],
    [
      ['查询', '点击"查询"按钮', '按条件筛选，结果在列表中展示，分页同步更新', '查无此项', '列表清空，展示"暂无要查询的数据"'],
      ['查询', '点击"查询"按钮', '查询成功，结果在列表中展示', '接口异常', 'Toast提示"接口异常，请稍候再试"'],
      ['查看', '点击"查看"按钮', '弹出查看弹窗，展示当前完整信息（只读）', '无', '无'],
      ['修改', '点击"修改"按钮', '弹出编辑弹窗，反显可编辑信息', '无', '无'],
      ['删除', '点击"删除"按钮', '弹出确认框，确认后删除数据，列表自动刷新', '删除后未刷新', '删除后自动刷新列表，确保数据展示同步'],
      ['新增/修改保存', '点击"确定"按钮', '弹窗关闭，列表刷新，Toast提示"保存成功"', '保存失败', 'Toast提示"保存失败，请重试！"']
    ],
    [16, 18, 28, 14, 24]
  ));
  c.push(blank());

  // 七
  c.push(h2('七、弹窗说明'));

  c.push(h3('7.1 查看详情弹窗'));
  c.push(h4('7.1.1 弹窗整体布局'));
  c.push(body('1. 弹窗标题区：显示"查看【替换】信息"，右上角提供关闭按钮（×）；'));
  c.push(body('2. 信息展示区：采用两列网格布局，只读展示所有字段；'));
  c.push(body('3. 操作按钮区：弹窗底部右侧仅展示"关闭"按钮。'));
  c.push(h4('7.1.2 展示字段说明'));
  c.push(makeTable(
    ['展示字段', '组件类型', '状态', '说明'],
    [
      ['【替换】字段1', '文本', '只读', '【替换】字段说明'],
      ['【替换】字段2', '文本', '只读', '【替换】字段说明'],
      ['添加时间', '文本', '只读', '格式 YYYY-MM-DD HH:mm:ss']
    ],
    [25, 18, 12, 45]
  ));
  c.push(blank());

  c.push(h3('7.2 新增/编辑弹窗'));
  c.push(h4('7.2.1 弹窗整体布局'));
  c.push(body('1. 弹窗标题区：新增时显示"新增【替换】"，编辑时显示"编辑【替换】信息"，右上角提供关闭按钮（×）；'));
  c.push(body('2. 表单录入区：采用两列布局，左右列水平均分，所有必填字段标注"*"；'));
  c.push(body('3. 操作按钮区：弹窗底部右侧"取消"+"确定"按钮。'));
  c.push(h4('7.2.2 录入字段说明'));
  c.push(makeTable(
    ['录入字段', '组件类型', '列位置', '初始状态', '约束规则', '举例'],
    [
      ['【替换】字段1', '输入框', '左侧', '可编辑，标注*', '非空；【替换】约束规则', '【替换】示例'],
      ['【替换】字段2', '下拉列表', '左侧', '可选择，标注*', '非空；数据源见第十二章', '【替换】示例'],
      ['【替换】字段3（只读）', '文本（只读）', '右侧', '只读，提示"【替换】自动生成"', '系统自动分配，不可手动修改', '【替换】示例']
    ],
    [20, 14, 10, 18, 24, 14]
  ));
  c.push(h4('7.2.3 操作按钮区'));
  c.push(makeTable(
    ['按钮', '组件类型', '初始状态', '约束规则'],
    [
      ['取消', '按钮', '可用', '点击后关闭弹窗，不保存任何未提交内容，无校验逻辑'],
      ['确定', '按钮', '默认灰化', '待所有必填字段填写合规后自动激活；点击触发全量校验，通过则保存并关闭弹窗']
    ],
    [15, 15, 15, 55]
  ));
  c.push(h4('7.2.4 弹窗交互规则'));
  c.push(body('交互逻辑遵循"即时校验、友好提示、操作闭环"原则。'));
  c.push(makeTable(
    ['交互类型', '正向交互', '异常交互'],
    [
      ['【替换】字段1输入', '非空且符合规则，失焦无错误提示', '失焦格式错误：输入框变红+下方红字提示错误原因；修正后提示自动消失'],
      ['【替换】字段2选择', '选择非空选项', '空值时下拉框变红+下方红字"请选择【替换】字段2"；修正后提示消失']
    ],
    [25, 30, 45]
  ));
  c.push(blank());

  c.push(h3('7.3 批量导入弹窗'));
  c.push(h4('7.3.1 弹窗整体布局'));
  c.push(body('1. 弹窗标题区：显示"批量导入"，右上角提供关闭按钮（×）；'));
  c.push(body('2. 上传区：支持点击选择文件或拖拽上传，仅接受 .xlsx 格式；'));
  c.push(body('3. 进度展示区：上传并处理时显示进度条及进度百分比；'));
  c.push(body('4. 操作按钮区：底部右侧"取消"+"开始导入"按钮；未选择文件时"开始导入"灰化不可点击。'));
  c.push(h4('7.3.2 导入规则'));
  c.push(makeTable(
    ['规则项', '说明'],
    [
      ['文件格式', '仅支持 .xlsx 文件'],
      ['模板要求', '使用系统提供的批量导入模板，字段与系统定义一致'],
      ['必填项', '【替换】列出必填字段'],
      ['成功处理', '导入完成后弹出结果提示，展示成功条数'],
      ['失败处理', '必填项不完整时提示"导入完成，失败X条，成功Y条，请检查后重新导入"']
    ],
    [25, 75]
  ));
  c.push(h4('7.3.3 导入模板字段说明'));
  c.push(makeTable(
    ['字段名称', '是否必填', '填写规则', '示例'],
    [
      ['【替换】字段1', '是', '【替换】填写规则', '【替换】示例值'],
      ['【替换】字段2', '是', '从下拉列表选择"【替换】选项"', '【替换】选项A']
    ],
    [22, 12, 40, 26]
  ));
  c.push(blank());

  // 八
  c.push(h2('八、错误处理规范'));
  c.push(h3('8.1 表单校验错误'));
  c.push(body('显示方式：对应字段下方显示红色提示文本，字段边框变红'));
  c.push(body('触发时机：表单提交时触发全量校验；字段失去焦点时触发单字段校验'));
  c.push(makeTable(
    ['字段', '为空时错误信息', '格式错误时信息'],
    [
      ['【替换】字段1', '【替换】字段1不能为空', '【替换】字段1格式不正确，应为xx'],
      ['【替换】字段2', '请选择【替换】字段2', '—']
    ],
    [25, 40, 35]
  ));
  c.push(blank());
  c.push(h3('8.2 文件操作错误'));
  c.push(makeTable(
    ['场景', '触发条件', '提示文案', '处理方式'],
    [
      ['导入-格式错误', '上传非 .xlsx 文件', '请上传正确格式的 Excel 文件', 'Toast 提示，阻断上传'],
      ['导入-超大文件', '文件超过 10MB', '文件大小不能超过 10MB', 'Toast 提示，阻断上传'],
      ['导入-数据错误', '存在不符合格式要求的数据行', '导入完成，失败N条，请检查后重新导入', '弹窗提示，展示失败详情'],
      ['导出-无数据', '当前查询结果为空', '暂无数据可导出', 'Toast 提示'],
      ['网络/服务异常', '接口请求失败', '接口异常，请稍候再试', 'Toast 提示']
    ],
    [18, 27, 32, 23]
  ));
  c.push(blank());

  // 九
  c.push(h2('九、接口规范'));
  c.push(body('【删除】列出本功能涉及的接口清单，供开发人员参考设计。接口详细入参/出参由后端开发定义。', { italic: true }));
  c.push(makeTable(
    ['接口名称', '请求方式', '接口路径', '备注'],
    [
      ['【替换】列表查询', 'GET', '/api/【替换】/page', '支持查询条件过滤，需分页'],
      ['新增', 'POST', '/api/【替换】/add', '—'],
      ['修改', 'PUT', '/api/【替换】/update', '—'],
      ['删除', 'DELETE', '/api/【替换】/delete', '支持批量删除'],
      ['导入', 'POST', '/api/【替换】/import', '上传 Excel 文件'],
      ['导出', 'GET', '/api/【替换】/export', '返回 Excel 文件']
    ],
    [22, 12, 36, 30]
  ));
  c.push(blank());

  // 十
  c.push(h2('十、非功能性需求'));
  c.push(h3('10.1 等保三级合规规范引用'));
  c.push(body('【删除】根据本模块实际情况，从下表选填适用章节，并在"本模块特有说明"中补充具体参数。不适用的行可删除。', { italic: true }));
  c.push(body('本模块适用以下通用安全规范，详细规则见《统一运营系统-等保三级通用安全要求》：'));
  c.push(makeTable(
    ['适用章节', '内容摘要', '本模块特有说明'],
    [
      ['§二 访问控制', 'RBAC最小权限、数据权限隔离', '【替换】如：机构管理员仅可查看本机构数据'],
      ['§三 操作日志规范', '字段级日志、保留≥6个月、不可篡改', '【替换】覆盖操作：新增/修改/删除/…（按实际填写）'],
      ['§四 敏感数据脱敏', '各字段脱敏规则', '【替换】如：手机号脱敏；或：本模块无敏感字段，不适用'],
      ['§五 文件操作安全', '导出上限、下载鉴权、导出行为记日志', '【替换】如：单次导出上限5000条；或：本模块无导出，不适用']
    ],
    [25, 35, 40]
  ));
  c.push(blank());
  c.push(h3('10.2 性能需求'));
  c.push(body('【删除】列出本模块的性能指标要求，填写实际约束；通用默认值可直接使用，有特殊要求的模块按实际填写。', { italic: true }));
  c.push(makeTable(
    ['需求项', '指标要求', '说明'],
    [
      ['列表查询响应时间', '≤ 2s', '正常网络条件下，含分页查询'],
      ['保存/提交响应时间', '≤ 3s', '新增/修改/删除等写操作'],
      ['导出响应时间', '≤ 5s（1000条以内）', '超出时建议提示异步处理'],
      ['页面首屏加载时间', '≤ 3s', '—'],
      ['并发用户数', '【替换】', '按实际业务填写']
    ],
    [38, 27, 35]
  ));
  c.push(blank());

  // 十一
  c.push(h2('十一、特殊说明'));
  c.push(body('【删除】补充业务逻辑特殊约束、编码规则、联动关系、删除/修改限制等，不适合放在上方章节的内容写在这里。', { italic: true }));
  c.push(h3('11.1 【替换】编码规则'));
  c.push(makeTable(
    ['项目', '规则说明'],
    [
      ['编码格式', '【替换】固定前缀 + 位数序号'],
      ['起始序号', '【替换】从"0001"开始'],
      ['完整示例', '【替换】XX0001、XX0002'],
      ['唯一性', '唯一标识，不可重复'],
      ['生成方式', '系统自动生成，不可手动输入或修改']
    ],
    [30, 70]
  ));
  c.push(h3('11.2 【替换】删除及修改限制'));
  c.push(body('【替换】说明当前记录在什么情况下不允许删除或修改，例如：已被其他模块引用时，按钮灰化置灰，不可操作；查看操作始终可用。'));
  c.push(h3('11.3 【替换】其他特殊规则'));
  c.push(body('1. 【替换】特殊规则1：说明业务约束或联动逻辑'));
  c.push(body('2. 【替换】特殊规则2：说明唯一性或数据生命周期'));
  c.push(blank());

  // 十二
  c.push(h2('十二、数据字典'));
  c.push(body('【删除】集中定义本功能中所有枚举/字典值，供前端枚举映射和开发智能体读取。', { italic: true }));
  c.push(h3('12.1 字典项定义'));
  c.push(body('【替换】状态字段（xxxStatus）', { bold: true }));
  c.push(makeTable(
    ['枚举值（code）', '显示文本（label）', '说明'],
    [
      ['0', '【替换】状态A', '【替换】说明'],
      ['1', '【替换】状态B', '【替换】说明']
    ],
    [20, 35, 45]
  ));
  c.push(blank());
  c.push(body('【替换】类型字段（xxxType）', { bold: true }));
  c.push(makeTable(
    ['枚举值（code）', '显示文本（label）', '说明'],
    [
      ['1', '【替换】类型A', '【替换】说明'],
      ['2', '【替换】类型B', '【替换】说明']
    ],
    [20, 35, 45]
  ));
  c.push(blank());
  c.push(h3('12.2 下拉框数据来源说明'));
  c.push(makeTable(
    ['字段名', '数据来源类型', '来源说明'],
    [
      ['【替换】字段1', '字典项', '参见 12.1 xxxStatus'],
      ['【替换】字段2', '接口动态加载', '来源：【替换】管理模块接口 /api/xxx/list']
    ],
    [30, 25, 45]
  ));

  return new Document({
    sections: [{
      properties: {
        page: {
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
          size: { width: 11906, height: 16838 }
        }
      },
      children: c
    }]
  });
}

function nextVersion(outDir, basename) {
  const files = fs.readdirSync(outDir);
  const re = new RegExp(`^${basename.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}_v(\\d+)\\.(\\d+)\\.(docx|md)$`);
  let maxMajor = 0, maxMinor = 0;
  files.forEach(f => {
    const m = f.match(re);
    if (m) {
      const major = parseInt(m[1]), minor = parseInt(m[2]);
      if (major > maxMajor || (major === maxMajor && minor > maxMinor)) {
        maxMajor = major; maxMinor = minor;
      }
    }
  });
  if (maxMajor === 0 && maxMinor === 0) return 'v0.1';
  return `v${maxMajor}.${maxMinor + 1}`;
}

async function main() {
  // 优先读取环境变量 DOC_DIR，否则使用当前工作目录下的 tongyiyunying/doc
  const outDir = process.env.DOC_DIR || require('path').join(process.cwd(), 'tongyiyunying', 'doc');
  const basename = 'AI智能体-统一运营系统-xxxxx功能设计模板';
  const ver = nextVersion(outDir, basename);

  // 生成 docx
  const docxName = `${basename}_${ver}.docx`;
  const buf = await docx.Packer.toBuffer(buildTemplate());
  fs.writeFileSync(path.join(outDir, docxName), buf);
  console.log(`✓ ${docxName}`);

  // 同步复制 .md
  const mdSrc = path.join(outDir, `${basename}.md`);
  if (fs.existsSync(mdSrc)) {
    const mdName = `${basename}_${ver}.md`;
    fs.copyFileSync(mdSrc, path.join(outDir, mdName));
    console.log(`✓ ${mdName}`);
  }
}

main().catch(console.error);
