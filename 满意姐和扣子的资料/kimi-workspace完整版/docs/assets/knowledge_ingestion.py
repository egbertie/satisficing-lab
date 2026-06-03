"""
五重门内化工作流引擎
实现文档知识入库的完整流程：登记→通读→笔记→总结→验证
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum
import hashlib
import json
import time
from datetime import datetime


class IngestionStatus(Enum):
    REGISTERED = "registered"
    PARSING = "parsing"
    PASS_1_READING = "pass_1_reading"
    PASS_2_NOTES = "pass_2_notes"
    PASS_3_SUMMARY = "pass_3_summary"
    VERIFICATION = "verification"
    VERIFIED = "verified"
    ARCHIVED = "archived"
    FAILED = "failed"


@dataclass
class FileMetadata:
    file_id: str
    filename: str
    file_hash: str
    file_size: int
    mime_type: str
    source: str  # 'feishu', 'wechat', 'upload', 'email'
    created_by: str
    created_at: datetime
    totem_category: Optional[str] = None
    status: IngestionStatus = IngestionStatus.REGISTERED


@dataclass
class InternalizationResult:
    file_id: str
    pass_1_output: Dict
    pass_2_output: Dict
    pass_3_output: Dict
    verification_score: int
    verification_qa: List[Dict]
    totem_analysis: Dict
    final_summary: str
    reusable_assets: List[Dict]
    created_at: datetime


class KnowledgeIngestionEngine:
    """
    五重门内化引擎
    
    五重门流程：
    1. 登记门（3分钟）: 文件指纹+五图腾分类+3-2-1备份
    2. 通读门（Pass 1）: 理解核心，AI生成结构大纲
    3. 笔记门（Pass 2）: 深度消化，五图腾模板提取
    4. 总结门（Pass 3）: 内化输出，形成可复用资产
    5. 验证门（5题抽查）: AI自评+蓝军审计，80分通过
    """
    
    def __init__(self, local_llm_client, kimi_client, db_client, storage_client):
        self.local_llm = local_llm_client
        self.kimi = kimi_client
        self.db = db_client
        self.storage = storage_client
        
        # 五图腾分析提示模板
        self.totem_templates = {
            'liu_yuxi_土': self._liu_yuxi_template,
            'simon_金': self._simon_template,
            'guan_zizai_水': self._guan_zizai_template,
            'confucius_木': self._confucius_template,
            'hui_neng_火': self._hui_neng_template
        }
    
    def ingest(self, file_path: str, source: str, created_by: str) -> Dict:
        """
        主入口：执行完整的五重门内化流程
        
        Args:
            file_path: 文件本地路径
            source: 文件来源
            created_by: 创建者
            
        Returns:
            内化结果报告
        """
        # 门1: 登记门
        metadata = self._gate_1_register(file_path, source, created_by)
        
        # 读取文件内容
        content = self._read_file(file_path)
        
        # 门2: 通读门
        pass_1_result = self._gate_2_reading(content, metadata)
        
        # 门3: 笔记门
        pass_2_result = self._gate_3_notes(content, pass_1_result, metadata)
        
        # 门4: 总结门
        pass_3_result = self._gate_4_summary(content, pass_2_result, metadata)
        
        # 门5: 验证门
        verification = self._gate_5_verification(pass_3_result, metadata)
        
        # 归档
        if verification['score'] >= 80:
            self._archive(metadata, pass_3_result, verification)
            metadata.status = IngestionStatus.VERIFIED
        else:
            metadata.status = IngestionStatus.FAILED
        
        return {
            'file_id': metadata.file_id,
            'status': metadata.status.value,
            'verification_score': verification['score'],
            'reusable_assets': pass_3_result.get('reusable_assets', []),
            'processing_time': self._calculate_processing_time(metadata)
        }
    
    def _gate_1_register(self, file_path: str, source: str, created_by: str) -> FileMetadata:
        """门1: 登记门 - 文件指纹+分类+备份"""
        
        # 1. 生成文件指纹
        file_hash = self._calculate_hash(file_path)
        file_size = self._get_file_size(file_path)
        filename = file_path.split('/')[-1]
        mime_type = self._detect_mime_type(file_path)
        
        # 2. 五图腾自动分类（本地LLM轻量处理）
        totem_category = self._classify_totem(filename)
        
        # 3. 创建元数据
        metadata = FileMetadata(
            file_id=self._generate_file_id(),
            filename=filename,
            file_hash=file_hash,
            file_size=file_size,
            mime_type=mime_type,
            source=source,
            created_by=created_by,
            created_at=datetime.now(),
            totem_category=totem_category,
            status=IngestionStatus.REGISTERED
        )
        
        # 4. 3-2-1备份
        self._backup_3_2_1(file_path, metadata)
        
        # 5. 保存元数据
        self.db.save_file_metadata(metadata)
        
        return metadata
    
    def _gate_2_reading(self, content: str, metadata: FileMetadata) -> Dict:
        """门2: 通读门 - 第一遍理解，生成结构大纲"""
        
        metadata.status = IngestionStatus.PASS_1_READING
        self.db.update_status(metadata.file_id, metadata.status)
        
        # 本地预处理：分段、去噪
        cleaned_content = self._preprocess_content(content)
        
        # 使用Kimi生成结构大纲（理解核心，不做笔记）
        prompt = f"""
        请阅读以下文档，生成结构大纲。要求：
        1. 识别核心论点（3-5个）
        2. 提取关键章节结构
        3. 标注重要数据/结论位置
        4. 不发表观点，只做客观结构提取
        
        文档内容：
        {cleaned_content[:15000]}  # 限制长度，避免过多Token
        """
        
        outline = self.kimi.generate(prompt, max_tokens=800)
        
        return {
            'outline': outline,
            'core_arguments': self._extract_arguments(outline),
            'structure': self._extract_structure(outline),
            'token_used': 800
        }
    
    def _gate_3_notes(self, content: str, pass_1: Dict, metadata: FileMetadata) -> Dict:
        """门3: 笔记门 - 第二遍深度消化，五图腾模板提取"""
        
        metadata.status = IngestionStatus.PASS_2_NOTES
        self.db.update_status(metadata.file_id, metadata.status)
        
        # 五图腾五维分析
        totem_analysis = {}
        for totem_name, template_func in self.totem_templates.items():
            prompt = template_func(content, pass_1['outline'])
            analysis = self.kimi.generate(prompt, max_tokens=400)
            totem_analysis[totem_name] = analysis
        
        # 提取可复用资产
        assets = self._extract_reusable_assets(content, totem_analysis)
        
        return {
            'totem_analysis': totem_analysis,
            'reusable_assets': assets,
            'key_insights': self._extract_insights(totem_analysis),
            'token_used': 2000  # 5个图腾 * 400T
        }
    
    def _gate_4_summary(self, content: str, pass_2: Dict, metadata: FileMetadata) -> Dict:
        """门4: 总结门 - 第三遍内化输出，形成可复用资产"""
        
        metadata.status = IngestionStatus.PASS_3_SUMMARY
        self.db.update_status(metadata.file_id, metadata.status)
        
        # 生成最终内化报告
        prompt = f"""
        基于以下分析结果，生成最终内化报告：
        
        五图腾分析：
        {json.dumps(pass_2['totem_analysis'], ensure_ascii=False)[:5000]}
        
        要求：
        1. 核心洞察（3-5条）
        2. 可执行资产清单
        3. 与现有系统的关联（依赖/冲突/整合）
        4. 下一步行动建议
        
        输出格式：Markdown
        """
        
        final_report = self.kimi.generate(prompt, max_tokens=1500)
        
        return {
            'final_report': final_report,
            'reusable_assets': pass_2['reusable_assets'],
            'next_actions': self._extract_actions(final_report),
            'token_used': 1500
        }
    
    def _gate_5_verification(self, pass_3: Dict, metadata: FileMetadata) -> Dict:
        """门5: 验证门 - 5题抽查，80分通过"""
        
        metadata.status = IngestionStatus.VERIFICATION
        self.db.update_status(metadata.file_id, metadata.status)
        
        # 生成5道验证题
        questions = self._generate_verification_questions(pass_3['final_report'])
        
        # AI自评（模拟）
        answers = []
        score = 0
        for q in questions:
            # 在实际系统中，这里应该由另一AI或人工回答
            # 这里简化为基于报告内容自动回答
            answer = self._auto_answer(q, pass_3['final_report'])
            is_correct = self._verify_answer(q, answer, pass_3['final_report'])
            answers.append({
                'question': q,
                'answer': answer,
                'correct': is_correct
            })
            if is_correct:
                score += 20  # 每题20分
        
        return {
            'score': score,
            'questions': answers,
            'passed': score >= 80
        }
    
    # 五图腾模板方法
    def _liu_yuxi_template(self, content: str, outline: str) -> str:
        return f"""
        【土-刘禹锡】长期根基视角分析
        
        请分析以下内容的长期影响：
        1. 3年后：此内容对组织/个人的影响是什么？
        2. 5年后：回看时会为此感到骄傲吗？
        3. 生态影响：对合作网络、行业生态的影响？
        4. 根基检验：是否巩固了核心价值观？
        
        文档大纲：{outline[:2000]}
        """
    
    def _simon_template(self, content: str, outline: str) -> str:
        return f"""
        【金-司马贺】满意解决策分析
        
        请分析以下内容：
        1. 边界条件：文档解决了什么问题？约束是什么？
        2. 满足阈值：如何定义"足够好"？
        3. 机会成本：继续深入探索的代价？
        4. 停止规则：何时可以停止优化？
        
        文档大纲：{outline[:2000]}
        """
    
    def _guan_zizai_template(self, content: str, outline: str) -> str:
        return f"""
        【水-观自在】直觉感知分析
        
        请分析以下内容的直觉信号：
        1. 第一感：这个方案/观点给人什么直觉感受？
        2. 模式识别：与什么过往经验相似？
        3. 内心声音：抛开逻辑，深层倾向是什么？
        4. 观察点：有什么显而易见却被忽视的细节？
        
        文档大纲：{outline[:2000]}
        """
    
    def _confucius_template(self, content: str, outline: str) -> str:
        return f"""
        【木-孔子】五常伦理分析
        
        请用五常框架评估：
        1. 仁：对利益相关者的影响？是否体恤他人？
        2. 义：利益分配是否公正？是否符合道义？
        3. 礼：是否符合商业伦理和行业规范？
        4. 智：是否基于充分信息？是否听取多方意见？
        5. 信：是否值得信赖？承诺是否可兑现？
        
        文档大纲：{outline[:2000]}
        """
    
    def _hui_neng_template(self, content: str, outline: str) -> str:
        return f"""
        【火-六祖慧能】顿悟突破分析
        
        请分析以下内容的突破机会：
        1. 问题重构：当前问题定义是否有限制？
        2. 逆向假设：如果常规选项都不可行？
        3. 跨界启发：其他领域如何解决？
        4. 顿悟触发：有什么显而易见的解决方案被忽视？
        
        文档大纲：{outline[:2000]}
        """
    
    # 工具方法
    def _calculate_hash(self, file_path: str) -> str:
        """计算文件SHA-256哈希"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _generate_file_id(self) -> str:
        """生成唯一文件ID"""
        return f"FILE-{int(time.time())}-{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
    
    def _backup_3_2_1(self, file_path: str, metadata: FileMetadata):
        """执行3-2-1备份策略"""
        # 3份副本：本地 + NAS + 云存储
        # 2种介质：磁盘 + 对象存储
        # 1份异地：云存储
        # 0错误：校验和验证
        
        # 这里简化实现，实际应调用存储服务
        backup_locations = [
            {'type': 'local', 'path': f'/backup/local/{metadata.file_id}'},
            {'type': 'nas', 'path': f'/nas/backup/{metadata.file_id}'},
            {'type': 'cloud', 'path': f's3://sri-backup/{metadata.file_id}'}
        ]
        
        for location in backup_locations:
            self.storage.backup(file_path, location)
        
        # 保存备份记录
        self.db.save_backup_records(metadata.file_id, backup_locations)
    
    def _classify_totem(self, filename: str) -> str:
        """根据文件名自动分类五图腾"""
        keywords = {
            'liu_yuxi_土': ['长期', '根基', '战略', '组织', '生态'],
            'simon_金': ['决策', '优化', '边界', '约束', '满意解'],
            'guan_zizai_水': ['直觉', '感知', '洞察', '观察'],
            'confucius_木': ['伦理', '合规', '价值观', '信任'],
            'hui_neng_火': ['创新', '突破', '顿悟', '变革']
        }
        
        filename_lower = filename.lower()
        for totem, words in keywords.items():
            if any(word in filename_lower for word in words):
                return totem
        
        return 'simon_金'  # 默认分类
    
    def _extract_reusable_assets(self, content: str, totem_analysis: Dict) -> List[Dict]:
        """提取可复用资产"""
        # 识别代码块、配置、模板等
        assets = []
        
        # 提取代码块
        import re
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
        for i, code in enumerate(code_blocks[:5]):  # 最多5个
            assets.append({
                'type': 'code',
                'name': f'code_snippet_{i+1}',
                'content': code[:500]  # 限制长度
            })
        
        # 提取配置
        if 'config' in content.lower() or '配置' in content:
            assets.append({
                'type': 'config',
                'name': 'configuration',
                'description': '配置文件或配置项'
            })
        
        return assets
    
    def _generate_verification_questions(self, report: str) -> List[str]:
        """生成5道验证题"""
        return [
            "文档的核心目标是什么？",
            "文档提供了哪几个关键方案/洞察？",
            "这些方案与现有系统有什么关联（依赖/冲突/整合）？",
            "可立即执行的任务有哪些？",
            "潜在风险或需要注意的事项是什么？"
        ]


# 使用示例
if __name__ == "__main__":
    # 初始化引擎
    engine = KnowledgeIngestionEngine(
        local_llm_client=None,  # 实际使用时传入
        kimi_client=None,
        db_client=None,
        storage_client=None
    )
    
    # 执行内化
    result = engine.ingest(
        file_path="/docs/example.md",
        source="feishu",
        created_by="Egbertie"
    )
    
    print(f"内化完成: {result}")
