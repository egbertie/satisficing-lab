#!/usr/bin/env python3
"""
Notion知识库第1批同步脚本 - 超小批次方案A
核心文档优先批次
"""
import json
import os
import time
import requests
from pathlib import Path
from datetime import datetime

# 配置
NOTION_TOKEN = "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"
PARENT_PAGE_ID = "31fa8a0e-2bba-81fa-b98a-d61da835051e"
RATE_LIMIT_MS = 350
WORKSPACE_DIR = Path("/root/.openclaw/workspace")
PROGRESS_FILE = WORKSPACE_DIR / ".notion_sync_v2_progress.json"
REPORT_FILE = WORKSPACE_DIR / "docs" / "NOTION_SYNC_BATCH_1_REPORT.md"

# 第1批文件列表（按优先级排序）
BATCH_1_FILES = [
    "docs/MANAGEMENT_RULES.md",
    "docs/TASK_MASTER.md",
    "docs/API_INVENTORY.md",
    "MEMORY.md",
    "SOUL.md",
    "USER.md",
    "AGENTS.md",
    "IDENTITY.md",
    "TOOLS.md",
    "BOOTSTRAP.md",
    "memory/2026-03-06.md",
    "memory/2026-03-07.md",
    "memory/2026-03-08.md",
    "memory/2026-03-09-回顾清单.md",
    "memory/2026-03-10.md",
    "WORKSPACE_STATUS.md",
]

class NotionBatch1Sync:
    def __init__(self):
        self.token = NOTION_TOKEN
        self.parent_id = PARENT_PAGE_ID
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.delay = RATE_LIMIT_MS / 1000
        self.stats = {
            "start_time": datetime.now(),
            "success": [],
            "failed": [],
            "skipped": []
        }
        
    def check_parent_page(self):
        """检查父页面是否存在"""
        url = f"https://api.notion.com/v1/pages/{self.parent_id}"
        try:
            resp = requests.get(url, headers=self.headers)
            time.sleep(self.delay)
            if resp.status_code == 200:
                return True, resp.json().get('url', 'unknown')
            return False, f"HTTP {resp.status_code}: {resp.text[:100]}"
        except Exception as e:
            return False, str(e)
    
    def read_file_content(self, file_path):
        """读取文件内容"""
        full_path = WORKSPACE_DIR / file_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read(), None
        except Exception as e:
            return None, str(e)
    
    def markdown_to_blocks(self, content):
        """将Markdown转换为Notion blocks"""
        blocks = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines) and len(blocks) < 95:  # 预留空间给额外block
            line = lines[i]
            
            # 代码块
            if line.strip().startswith('```'):
                lang = line.strip()[3:].strip() or "plain text"
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                code_content = '\n'.join(code_lines)[:1990]  # 接近限制但留余地
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": code_content}}],
                        "language": lang if lang in ["python", "javascript", "java", "json", "markdown", "bash", "sql", "html", "css", "typescript"] else "plain text"
                    }
                })
                i += 1
                continue
            
            # 标题
            if line.startswith('# ') and len(line) > 2:
                blocks.append({
                    "object": "block", "type": "heading_1",
                    "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:].strip()[:2000]}}]}
                })
            elif line.startswith('## ') and len(line) > 3:
                blocks.append({
                    "object": "block", "type": "heading_2",
                    "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:].strip()[:2000]}}]}
                })
            elif line.startswith('### ') and len(line) > 4:
                blocks.append({
                    "object": "block", "type": "heading_3",
                    "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:].strip()[:2000]}}]}
                })
            # 列表
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                blocks.append({
                    "object": "block", "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line.strip()[2:].strip()[:2000]}}]}
                })
            elif len(line.strip()) > 2 and line.strip()[0].isdigit() and line.strip()[1:3] == '. ':
                text = line.strip()[3:].strip()[:2000]
                blocks.append({
                    "object": "block", "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}
                })
            # 分隔线
            elif line.strip() == '---':
                blocks.append({"object": "block", "type": "divider", "divider": {}})
            # 引用
            elif line.strip().startswith('> '):
                blocks.append({
                    "object": "block", "type": "quote",
                    "quote": {"rich_text": [{"type": "text", "text": {"content": line.strip()[2:].strip()[:2000]}}]}
                })
            # 普通段落（非空行）
            elif line.strip():
                blocks.append({
                    "object": "block", "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": line.strip()[:2000]}}]}
                })
            
            i += 1
        
        # 如果内容被截断，添加提示
        if i < len(lines):
            blocks.append({
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": "...(内容已截断，原文件共" + str(len(lines)) + "行)"}}]}
            })
        
        return blocks
    
    def create_page(self, title, blocks, file_path):
        """创建Notion页面"""
        url = "https://api.notion.com/v1/pages"
        
        payload = {
            "parent": {"page_id": self.parent_id},
            "properties": {
                "title": {"title": [{"text": {"content": title[:100]}}]}
            },
            "children": blocks[:100]  # Notion API限制单次最多100个blocks
        }
        
        try:
            resp = requests.post(url, headers=self.headers, json=payload)
            time.sleep(self.delay)
            
            if resp.status_code in [200, 201]:
                data = resp.json()
                return {"success": True, "page_id": data.get('id'), "url": data.get('url')}
            else:
                return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sync_single_file(self, file_path, index, total):
        """同步单个文件"""
        print(f"[{index}/{total}] {file_path}...", end=" ")
        
        # 检查文件是否存在
        full_path = WORKSPACE_DIR / file_path
        if not full_path.exists():
            self.stats["skipped"].append({"file": file_path, "reason": "文件不存在"})
            print("⏭️ 跳过（不存在）")
            return
        
        # 读取内容
        content, error = self.read_file_content(file_path)
        if error:
            self.stats["failed"].append({"file": file_path, "reason": f"读取失败: {error}"})
            print(f"❌ 读取失败: {error}")
            return
        
        # 转换Markdown
        title = Path(file_path).stem[:100]
        blocks = self.markdown_to_blocks(content)
        
        # 创建页面
        result = self.create_page(title, blocks, file_path)
        
        if result["success"]:
            self.stats["success"].append({
                "file": file_path,
                "page_id": result["page_id"],
                "url": result["url"]
            })
            print(f"✅ 成功 (ID: {result['page_id'][:12]}...)")
        else:
            self.stats["failed"].append({
                "file": file_path,
                "reason": result["error"]
            })
            print(f"❌ 失败: {result['error'][:60]}")
    
    def run(self):
        """执行同步"""
        print("=" * 70)
        print("📚 Notion知识库第1批同步 (方案A - 超小批次)")
        print("=" * 70)
        print(f"开始时间: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"目标批次: 第1批 (核心文档)")
        print(f"文件数量: {len(BATCH_1_FILES)} 个")
        print(f"速率限制: {RATE_LIMIT_MS}ms/请求")
        print("-" * 70)
        
        # 1. 检查父页面
        print("\n🔍 检查父页面...", end=" ")
        exists, info = self.check_parent_page()
        if exists:
            print(f"✅ 存在 ({info})")
        else:
            print(f"⚠️ 可能不存在: {info}")
        print(f"   父页面ID: {self.parent_id}")
        
        # 2. 同步文件
        print("\n" + "-" * 70)
        print("开始同步文件...")
        print("-" * 70)
        
        for i, file_path in enumerate(BATCH_1_FILES, 1):
            self.sync_single_file(file_path, i, len(BATCH_1_FILES))
        
        # 3. 计算统计
        end_time = datetime.now()
        duration = (end_time - self.stats["start_time"]).total_seconds()
        
        print("\n" + "=" * 70)
        print("📊 同步完成统计")
        print("=" * 70)
        print(f"✅ 成功: {len(self.stats['success'])} 个")
        print(f"❌ 失败: {len(self.stats['failed'])} 个")
        print(f"⏭️ 跳过: {len(self.stats['skipped'])} 个")
        print(f"⏱️ 用时: {duration:.1f} 秒 ({duration/60:.1f} 分钟)")
        print(f"📝 平均每文件: {duration/max(len(self.stats['success']), 1):.1f} 秒")
        
        return duration
    
    def save_progress(self):
        """保存进度文件"""
        progress = {
            "total_files": 263,
            "batch_size": 20,
            "total_batches": 14,
            "current_batch": 1,
            "completed_files": [item["file"] for item in self.stats["success"]],
            "failed_files": self.stats["failed"],
            "skipped_files": self.stats["skipped"],
            "in_progress": False,
            "notion_parent_page_id": PARENT_PAGE_ID,
            "last_sync": datetime.now().isoformat()
        }
        
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 进度已保存: {PROGRESS_FILE}")
    
    def generate_report(self, duration):
        """生成报告"""
        end_time = datetime.now()
        
        report_lines = [
            "# Notion知识库同步报告 - 第1批",
            "",
            f"**同步时间**: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**批次**: 第1批 (核心文档)",
            f"**策略**: 超小批次方案A",
            "",
            "## 执行摘要",
            "",
            f"- **成功**: {len(self.stats['success'])} 个文件",
            f"- **失败**: {len(self.stats['failed'])} 个文件",
            f"- **跳过**: {len(self.stats['skipped'])} 个文件",
            f"- **总用时**: {duration:.1f} 秒 ({duration/60:.1f} 分钟)",
            f"- **平均速度**: {duration/max(len(self.stats['success']), 1):.1f} 秒/文件",
            "",
            "## 成功同步的文件",
            ""
        ]
        
        for item in self.stats["success"]:
            report_lines.append(f"- ✅ `{item['file']}` → [{item['page_id'][:12]}...]({item.get('url', '#')})")
        
        if self.stats["failed"]:
            report_lines.extend([
                "",
                "## 失败的文件",
                ""
            ])
            for item in self.stats["failed"]:
                report_lines.append(f"- ❌ `{item['file']}`: {item['reason']}")
        
        if self.stats["skipped"]:
            report_lines.extend([
                "",
                "## 跳过的文件",
                ""
            ])
            for item in self.stats["skipped"]:
                report_lines.append(f"- ⏭️ `{item['file']}`: {item['reason']}")
        
        # 预估剩余时间
        remaining_files = 263 - len(self.stats["success"]) - len(self.stats["skipped"])
        avg_time = duration / max(len(self.stats["success"]), 1)
        est_remaining_batches = (remaining_files / 18)  # 平均每批18个
        est_remaining_time = remaining_files * avg_time / 60  # 分钟
        
        report_lines.extend([
            "",
            "## 进度预估",
            "",
            f"- **已完成**: {len(self.stats['success'])} / 263 个文件 ({len(self.stats['success'])/263*100:.1f}%)",
            f"- **剩余文件**: {remaining_files} 个",
            f"- **预估批次**: 约 {est_remaining_batches:.0f} 批",
            f"- **预估剩余时间**: 约 {est_remaining_time:.0f} 分钟 ({est_remaining_time/60:.1f} 小时)",
            "",
            "## 下一步建议",
            "",
            "1. **检查失败文件**: 查看失败原因，可能是网络问题或API限制",
            "2. **执行第2批**: 准备好后继续同步下一批文件",
            "3. **调整速率**: 如果仍然失败，考虑增加速率限制到500ms/请求",
            "4. **分批验证**: 定期检查Notion中页面是否正确创建",
            "",
            "---",
            f"*报告生成时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        # 确保docs目录存在
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"📝 报告已生成: {REPORT_FILE}")

def main():
    syncer = NotionBatch1Sync()
    duration = syncer.run()
    syncer.save_progress()
    syncer.generate_report(duration)
    print("\n" + "=" * 70)
    print("✨ 第1批同步任务完成!")
    print("=" * 70)

if __name__ == "__main__":
    main()
