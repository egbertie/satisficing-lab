const fs = require('fs');
const path = require('path');

const BASE_PATH = 'C:\\Users\\mengf\\.qclaw\\成果归档';
const INDEX_FILE = path.join(BASE_PATH, 'README.md');

/**
 * 获取下一个文章序号
 */
function getNextArticleNumber() {
    const articlePath = path.join(BASE_PATH, '文章');
    if (!fs.existsSync(articlePath)) {
        return 1;
    }
    
    const files = fs.readdirSync(articlePath);
    const numbers = files
        .filter(f => f.endsWith('.md'))
        .map(f => {
            const match = f.match(/^(\d+)-/);
            return match ? parseInt(match[1]) : 0;
        });
    
    return numbers.length > 0 ? Math.max(...numbers) + 1 : 1;
}

/**
 * 清理文件名中的非法字符
 */
function sanitizeFilename(title) {
    return title.replace(/[\\/:*?"<>|]/g, '').replace(/\s+/g, '-');
}

/**
 * 统计字数
 */
function countWords(content) {
    // 移除Markdown标记后统计中文字符和英文单词
    const cleanContent = content
        .replace(/#+\s/g, '')  // 移除标题标记
        .replace(/\*\*/g, '')   // 移除加粗标记
        .replace(/\*/g, '')     // 移除斜体标记
        .replace(/`{3}[\s\S]*?`{3}/g, '')  // 移除代码块
        .replace(/`([^`]+)`/g, '$1')  // 移除行内代码
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')  // 移除链接
        .replace(/!\[([^\]]*)\]\([^)]+\)/g, '');  // 移除图片
    
    const chineseChars = (cleanContent.match(/[\u4e00-\u9fa5]/g) || []).length;
    const englishWords = (cleanContent.match(/[a-zA-Z]+/g) || []).length;
    
    return chineseChars + englishWords;
}

/**
 * 内容检查
 */
function checkContent(content, type = 'article') {
    const issues = [];
    const wordCount = countWords(content);
    
    // 字数检查
    if (type === 'article' && wordCount < 1500) {
        issues.push(`字数不足：当前${wordCount}字，建议1500字以上`);
    }
    if (type === 'copy' && wordCount < 300) {
        issues.push(`字数不足：当前${wordCount}字，建议300字以上`);
    }
    
    // 检查金句（引号内的内容或加粗内容）
    const quotes = content.match(/"([^"]+)"/g) || [];
    const boldTexts = content.match(/\*\*([^*]+)\*\*/g) || [];
    if (quotes.length + boldTexts.length < 3) {
        issues.push('金句较少：建议增加3条以上金句（引号或加粗）');
    }
    
    // 检查数据（数字+单位）
    const dataPatterns = content.match(/\d+[%％亿万千元美元]+/g) || [];
    if (dataPatterns.length < 3) {
        issues.push('数据支撑不足：建议增加3个以上具体数据');
    }
    
    // 检查配图建议
    if (!content.includes('配图') && !content.includes('图片')) {
        issues.push('缺少配图建议：建议添加配图说明');
    }
    
    return {
        wordCount,
        issues,
        passed: issues.length === 0
    };
}

/**
 * 更新索引文件
 */
function updateIndex(title, filename, number) {
    const today = new Date();
    const yearMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    const date = `${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    
    let indexContent = '';
    
    if (fs.existsSync(INDEX_FILE)) {
        indexContent = fs.readFileSync(INDEX_FILE, 'utf8');
    } else {
        // 创建新的索引文件
        indexContent = `# 成果归档索引\n\n> 自动生成于 ${today.toISOString().split('T')[0]}\n> \n> 本索引记录所有保存的文章、文案和对话历史\n\n`;
    }
    
    // 检查是否已存在该月份
    const monthHeader = `## ${yearMonth}`;
    if (!indexContent.includes(monthHeader)) {
        indexContent += `\n${monthHeader}\n\n`;
        indexContent += `| 日期 | 序号 | 标题 | 文件 |\n`;
        indexContent += `|:---:|:---:|:---|:---|\n`;
    }
    
    // 添加新记录
    const newRow = `| ${date} | ${String(number).padStart(2, '0')} | ${title} | [${filename}](./文章/${filename}) |\n`;
    
    // 在月份表格末尾插入新行
    const monthRegex = new RegExp(`(## ${yearMonth}\\n\\n\\|[^\\n]+\\n\\|[^\\n]+\\n)`);
    if (monthRegex.test(indexContent)) {
        indexContent = indexContent.replace(monthRegex, `$1${newRow}`);
    } else {
        // 如果正则匹配失败，直接追加到文件末尾
        indexContent += newRow;
    }
    
    fs.writeFileSync(INDEX_FILE, indexContent, 'utf8');
    
    return { updated: true, path: INDEX_FILE };
}

/**
 * 生成归档报告
 */
function generateArchiveReport() {
    const today = new Date().toISOString().split('T')[0];
    
    // 统计文章
    const articlePath = path.join(BASE_PATH, '文章');
    const articles = fs.existsSync(articlePath) 
        ? fs.readdirSync(articlePath).filter(f => f.endsWith('.md'))
        : [];
    
    // 统计文案
    const copyPath = path.join(BASE_PATH, '文案');
    const copies = fs.existsSync(copyPath)
        ? fs.readdirSync(copyPath).filter(f => f.endsWith('.md') && f.includes(today))
        : [];
    
    // 统计历史
    const historyPath = path.join(BASE_PATH, '对话历史');
    const histories = fs.existsSync(historyPath)
        ? fs.readdirSync(historyPath).filter(f => f.endsWith('.md') && f.includes(today))
        : [];
    
    const report = {
        date: today,
        summary: {
            totalArticles: articles.length,
            todayCopies: copies.length,
            todayHistories: histories.length
        },
        articles: articles,
        todayCopies: copies,
        todayHistories: histories
    };
    
    return report;
}

/**
 * 保存文章
 */
function saveArticle(title, content, options = {}) {
    // 内容检查
    const check = checkContent(content, 'article');
    
    // 如果强制保存或检查通过，则保存
    if (!options.force && !check.passed) {
        return {
            success: false,
            message: '内容检查未通过',
            check: check,
            hint: '使用 force: true 强制保存，或根据提示修改内容'
        };
    }
    
    const num = getNextArticleNumber();
    const safeTitle = sanitizeFilename(title);
    const filename = `${String(num).padStart(2, '0')}-${safeTitle}.md`;
    const filepath = path.join(BASE_PATH, '文章', filename);
    
    fs.mkdirSync(path.dirname(filepath), { recursive: true });
    fs.writeFileSync(filepath, content, 'utf8');
    
    // 更新索引
    const indexResult = updateIndex(title, filename, num);
    
    return {
        success: true,
        path: filepath,
        filename,
        number: num,
        wordCount: check.wordCount,
        indexUpdated: indexResult.updated,
        indexPath: indexResult.path,
        warnings: check.issues.length > 0 ? check.issues : null
    };
}

/**
 * 保存文案
 */
function saveCopy(title, content, options = {}) {
    // 内容检查
    const check = checkContent(content, 'copy');
    
    if (!options.force && !check.passed) {
        return {
            success: false,
            message: '内容检查未通过',
            check: check,
            hint: '使用 force: true 强制保存，或根据提示修改内容'
        };
    }
    
    const today = new Date().toISOString().split('T')[0];
    const safeTitle = sanitizeFilename(title);
    const filename = `${today}_${safeTitle}_文案.md`;
    const filepath = path.join(BASE_PATH, '文案', filename);
    
    fs.mkdirSync(path.dirname(filepath), { recursive: true });
    fs.writeFileSync(filepath, content, 'utf8');
    
    return {
        success: true,
        path: filepath,
        filename,
        wordCount: check.wordCount,
        warnings: check.issues.length > 0 ? check.issues : null
    };
}

/**
 * 保存对话历史
 */
function saveHistory(content) {
    const today = new Date().toISOString().split('T')[0];
    const filename = `${today}_对话历史.md`;
    const filepath = path.join(BASE_PATH, '对话历史', filename);
    
    fs.mkdirSync(path.dirname(filepath), { recursive: true });
    fs.writeFileSync(filepath, content, 'utf8');
    
    return {
        success: true,
        path: filepath,
        filename
    };
}

/**
 * 批量保存今日成果
 */
function saveAllToday(articles = [], copies = [], history = '') {
    const results = {
        articles: [],
        copies: [],
        history: null,
        report: generateArchiveReport()
    };
    
    // 保存文章
    for (const article of articles) {
        const result = saveArticle(article.title, article.content, { force: true });
        results.articles.push(result);
    }
    
    // 保存文案
    for (const copy of copies) {
        const result = saveCopy(copy.title, copy.content, { force: true });
        results.copies.push(result);
    }
    
    // 保存对话历史
    if (history) {
        results.history = saveHistory(history);
    }
    
    return results;
}

// 导出函数供其他脚本使用
module.exports = {
    saveArticle,
    saveCopy,
    saveHistory,
    saveAllToday,
    getNextArticleNumber,
    checkContent,
    updateIndex,
    generateArchiveReport,
    countWords
};

// 如果直接运行此脚本
if (require.main === module) {
    const args = process.argv[2];
    if (!args) {
        console.log(JSON.stringify({ success: false, message: '缺少参数' }));
        process.exit(1);
    }
    
    try {
        const params = JSON.parse(args);
        
        let result;
        switch (params.type) {
            case 'article':
                result = saveArticle(params.title, params.content, { force: params.force });
                break;
            case 'copy':
                result = saveCopy(params.title, params.content, { force: params.force });
                break;
            case 'history':
                result = saveHistory(params.content);
                break;
            case 'report':
                result = generateArchiveReport();
                break;
            default:
                console.log(JSON.stringify({ success: false, message: '未知的保存类型: ' + params.type }));
                process.exit(1);
        }
        
        console.log(JSON.stringify(result));
    } catch (e) {
        console.log(JSON.stringify({ success: false, message: '错误: ' + e.message }));
        process.exit(1);
    }
}
