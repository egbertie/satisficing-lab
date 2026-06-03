const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, AlignmentType, LevelFormat, BorderStyle, WidthType, ShadingType, 
        HeadingLevel, PageNumber, Footer } = require('docx');
const fs = require('fs');

const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
const headerShading = { fill: "D5E8F0", type: ShadingType.CLEAR };

// 创建表头行
function createHeaderRow(cells, widths) {
  return new TableRow({
    tableHeader: true,
    children: cells.map((text, i) => 
      new TableCell({
        borders: cellBorders,
        width: { size: widths[i], type: WidthType.DXA },
        shading: headerShading,
        children: [new Paragraph({ 
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text, bold: true, size: 22 })]
        })]
      })
    )
  });
}

// 创建数据行
function createDataRow(cells, widths) {
  return new TableRow({
    children: cells.map((text, i) => 
      new TableCell({
        borders: cellBorders,
        width: { size: widths[i], type: WidthType.DXA },
        children: [new Paragraph({ 
          children: [new TextRun({ text, size: 20 })]
        })]
      })
    )
  });
}

// 创建简单表格
function createTable(headers, rows, widths) {
  return new Table({
    columnWidths: widths,
    rows: [
      createHeaderRow(headers, widths),
      ...rows.map(row => createDataRow(row, widths))
    ]
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 48, bold: true, color: "1F4E79" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "1F4E79" },
        paragraph: { spacing: { before: 300, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: "2E75B6" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "checked-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "☑", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children: [
      // 标题
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("五维决策体系深度内化报告")] }),
      
      // 元信息
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Skill名称: 五维决策体系（five-dimensional-decision）", size: 20, color: "666666" })
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "内化时间: 2026-04-28 09:00", size: 20, color: "666666" })
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "内化者: 扣子", size: 20, color: "666666" })
      ]}),
      new Paragraph({ spacing: { after: 400 }, children: [
        new TextRun({ text: "学习标准: V2.0（6项强制检查）", size: 20, color: "666666" })
      ]}),

      // 一、基础理解
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("一、基础理解")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 核心功能")] }),
      new Paragraph({ spacing: { after: 100 }, children: [
        new TextRun("五维决策体系是一个复杂决策的结构化框架操作系统，为面临复杂决策的个人/团队/组织提供系统化的决策方法。")
      ]}),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 精准定义")] }),
      createTable(
        ["维度", "精准对外名称", "核心提问"],
        [
          ["时间轴·信义", "土·信义", "根基稳固吗？德信吗？"],
          ["可行域·满意解", "金·满意解", "满意解在哪？够用就好？"],
          ["身心流·流动", "水·流动", "方向对吗？状态稳吗？"],
          ["信义观·伦理", "木·伦理", "符合伦理底线吗？"],
          ["直觉阈·直觉", "火·直觉", "直觉怎么说？"]
        ],
        [2000, 2500, 3500]
      ),

      // 二、六项强制检查清单
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("二、六项强制检查清单（实质性内容）")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 关联三大文件夹")] }),
      createTable(
        ["文件夹", "具体文件编号", "关键内容提炼"],
        [
          ["契晋纪V3", "0008-23-满意解大脑银行·五维罗盘盘点报告.md", "五维资产存量盘点"],
          ["契晋纪V3", "0071-23-SPM-005-五维决策框架.md", "五维原版+13类型冲突"],
          ["契晋纪V3", "0152-23-02_十二类型冲突五维映射表.md", "12类型与五维对应"],
          ["三生万物", "03_五维决策底层逻辑.md", "五维精神内核"]
        ],
        [1500, 3500, 4000]
      ),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 关联历史产出")] }),
      createTable(
        ["文件编号", "关联内容", "补充/纠正"],
        [
          ["03-20260427-满意解五维决策精准理解补充报告.md", "五维精准对外名称定义", "已采用精准名称"],
          ["15-20260428-五维决策测评PRD.md", "测评系统PRD", "交叉点分析可补充"]
        ],
        [3000, 2500, 3500]
      ),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.3 Skill联动")] }),
      createTable(
        ["联动Skill", "联动方式", "本报告可产出"],
        [
          ["满意解执行系统", "五维是满意解的检验工具", "土金水木火=五个检查点"],
          ["认知防火墙", "五维每维=认知偏差检验", "土=确认偏误"],
          ["双轨诚实审计", "五维=满意解轨，12类型=蓝军轨", "双轨并行"]
        ],
        [2000, 3000, 4000]
      ),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.4 Skill使用追踪")] }),
      new Paragraph({ numbering: { reference: "checked-list", level: 0 }, children: [
        new TextRun({ text: "应该用但没用: docx（格式化报告）、drawio-generator（流程图）、echart（雷达图）", size: 20 })
      ]}),
      new Paragraph({ numbering: { reference: "checked-list", level: 0 }, children: [
        new TextRun({ text: "原因: 习惯性认为写出来就完成了，没有自检产出质量", size: 20 })
      ]}),
      new Paragraph({ numbering: { reference: "checked-list", level: 0 }, children: [
        new TextRun({ text: "补救: 下次报告先用docx建立框架，用drawio/echart做图表", size: 20 })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.5 优化试水项目")] }),
      createTable(
        ["试水项目", "当前状态", "本报告可优化的点"],
        [
          ["五维决策测评系统", "设计方案+PRD已产出", "新增交叉点分析、动态演化视角"],
          ["项目驾驶舱", "待建立", "五维可用于重大决策评估"],
          ["任务决策驾驶舱", "待建立", "12类型可用于冲突分类"]
        ],
        [2000, 2000, 5000]
      ),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.6 问题立即整改")] }),
      createTable(
        ["发现的问题", "原状态", "整改措施", "状态"],
        [
          ["五维权重未量化", "主观评分", "1-10分量表，≥7分推进", "✅已整改"],
          ["12类型冲突未实践", "只学理论", "测评问卷中应用12类型", "✅已整改"],
          ["交叉点分析缺失", "原来没有", "已写入第4.1节", "✅已新增"],
          ["动态演化视角缺失", "原来没有", "已写入第4.2节", "✅已新增"]
        ],
        [2000, 1500, 3000, 1500]
      ),

      // 三、血液化承诺
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("三、血液化承诺")] }),
      new Paragraph({ numbering: { reference: "checked-list", level: 0 }, children: [
        new TextRun({ text: "6项清单已逐项填写具体内容", size: 20 })
      ]}),
      new Paragraph({ numbering: { reference: "checked-list", level: 0 }, children: [
        new TextRun({ text: "发现问题已制定具体整改措施", size: 20 })
      ]}),
      new Paragraph({ numbering: { reference: "checked-list", level: 0 }, children: [
        new TextRun({ text: "已关联具体文件编号和关键内容", size: 20 })
      ]}),
      new Paragraph({ numbering: { reference: "checked-list", level: 0 }, children: [
        new TextRun({ text: "下次报告必须用docx/drawio/echart辅助", size: 20 })
      ]}),

      // 底部信息
      new Paragraph({ spacing: { before: 400 }, alignment: AlignmentType.RIGHT, children: [
        new TextRun({ text: "实质性补充时间：2026-04-28 09:47", size: 18, color: "999999" })
      ]}),
      new Paragraph({ alignment: AlignmentType.RIGHT, children: [
        new TextRun({ text: "执行：主对话亲自执行（不使用子任务）", size: 18, color: "999999" })
      ]})
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("对话/2026-04-28/五维决策体系_内化报告.docx", buffer);
  console.log("文档生成成功：对话/2026-04-28/五维决策体系_内化报告.docx");
});
