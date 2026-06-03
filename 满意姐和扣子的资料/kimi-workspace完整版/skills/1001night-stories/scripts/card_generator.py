#!/usr/bin/env python3
"""
1001夜童话故事汇 - 卡牌与故事书生成器
支持生成游戏化学习材料
"""

import os
import json
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime


class CardGameGenerator:
    """卡牌游戏生成器"""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_knowledge_card(
        self,
        knowledge_point: str,
        knowledge_type: str,
        content: str,
        difficulty: str = "medium",
        bonus_effect: str = ""
    ) -> Dict[str, Any]:
        """
        生成知识卡牌
        
        Args:
            knowledge_point: 知识点名称
            knowledge_type: 知识类型 (concept/fact/process/person)
            content: 卡牌内容
            difficulty: 难度等级 (easy/medium/hard)
            bonus_effect: 奖励效果描述
        """
        # 根据知识类型设置卡牌属性
        type_properties = {
            "concept": {"color": "蓝色", "icon": "💡", "category": "概念"},
            "fact": {"color": "绿色", "icon": "📚", "category": "事实"},
            "process": {"color": "橙色", "icon": "🔄", "category": "过程"},
            "person": {"color": "紫色", "icon": "👤", "category": "人物"}
        }
        
        props = type_properties.get(knowledge_type, type_properties["concept"])
        
        # 难度系数
        difficulty_cards = {
            "easy": 1,
            "medium": 2,
            "hard": 3
        }
        
        card = {
            "name": knowledge_point,
            "type": props["category"],
            "type_icon": props["icon"],
            "content": content,
            "difficulty": difficulty,
            "difficulty_stars": difficulty_cards.get(difficulty, 2),
            "bonus_effect": bonus_effect,
            "color_theme": props["color"],
            "story_context": f"在{knowledge_point}的魔法世界里...",
            "illustration_prompt": self._build_card_prompt(knowledge_point, content)
        }
        
        return card
    
    def generate_character_card(
        self,
        name: str,
        role: str,
        abilities: List[str],
        story_background: str,
        visual_features: str
    ) -> Dict[str, Any]:
        """
        生成角色卡牌
        """
        card = {
            "name": name,
            "role": role,
            "abilities": abilities,
            "story_background": story_background,
            "visual_features": visual_features,
            "card_stats": {
                "power": len(abilities) * 10 + 50,
                "wisdom": 70,
                "creativity": 80
            },
            "illustration_prompt": self._build_character_prompt(name, visual_features, role),
            "ability_descriptions": [
                f"主动技能：{ability}" for ability in abilities
            ]
        }
        
        return card
    
    def generate_challenge_card(
        self,
        challenge_name: str,
        knowledge_required: List[str],
        description: str,
        rewards: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成挑战卡牌
        """
        card = {
            "name": challenge_name,
            "type": "challenge",
            "type_icon": "⚔️",
            "knowledge_required": knowledge_required,
            "description": description,
            "rewards": rewards,
            "difficulty": len(knowledge_required),
            "illustration_prompt": self._build_challenge_prompt(challenge_name, description)
        }
        
        return card
    
    def _build_card_prompt(self, subject: str, content: str) -> str:
        """构建卡牌插图prompt"""
        return f"童话风格知识卡牌插图，主题：{subject}，内容：{content[:50]}，风格：精美绘本插画，温暖色调，卡通风格"
    
    def _build_character_prompt(self, name: str, features: str, role: str) -> str:
        """构建角色卡牌插图prompt"""
        return f"童话风格角色卡牌，角色名：{name}，特征：{features}，身份：{role}，风格：精美绘本插画，角色立绘"
    
    def _build_challenge_prompt(self, challenge: str, description: str) -> str:
        """构建挑战卡牌插图prompt"""
        return f"童话风格冒险场景，挑战：{challenge}，描述：{description[:30]}，风格：精美绘本插画，冒险主题"
    
    def export_to_json(self, cards: List[Dict], filename: str = "cards.json") -> str:
        """导出卡牌到JSON"""
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_cards": len(cards),
                "cards": cards
            }, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def export_to_markdown(self, cards: List[Dict], filename: str = "cards.md") -> str:
        """导出卡牌到Markdown格式"""
        output_path = os.path.join(self.output_dir, filename)
        
        lines = [
            "# 1001夜知识卡牌集",
            "",
            f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"卡牌总数：{len(cards)}",
            "",
            "---",
            ""
        ]
        
        for i, card in enumerate(cards, 1):
            lines.append(f"## 卡牌 #{i}: {card.get('name', '未知')}")
            lines.append("")
            
            for key, value in card.items():
                if key == "illustration_prompt":
                    continue
                if isinstance(value, list):
                    lines.append(f"- **{key}**: {', '.join(str(v) for v in value)}")
                else:
                    lines.append(f"- **type**: {value}")
            
            lines.append("")
            lines.append(f"*[插图提示]: {card.get('illustration_prompt', '')}")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return output_path


class StoryBookGenerator:
    """故事书生成器"""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_story_page(
        self,
        page_number: int,
        title: str,
        content: str,
        illustration_prompt: str,
        knowledge_notes: Optional[List[str]] = None,
        game_elements: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        生成故事书单页
        """
        page = {
            "page_number": page_number,
            "title": title,
            "content": content,
            "illustration_prompt": illustration_prompt,
            "knowledge_notes": knowledge_notes or [],
            "game_elements": game_elements or {},
            "reading_time": f"{len(content) // 100 + 1}分钟"
        }
        
        return page
    
    def generate_story_chapter(
        self,
        chapter_number: int,
        chapter_title: str,
        pages: List[Dict[str, Any]],
        knowledge_summary: List[str]
    ) -> Dict[str, Any]:
        """
        生成故事章节
        """
        chapter = {
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "pages": pages,
            "knowledge_summary": knowledge_summary,
            "total_pages": len(pages),
            "total_knowledge_points": len(knowledge_summary)
        }
        
        return chapter
    
    def export_storybook(
        self,
        title: str,
        subtitle: str,
        chapters: List[Dict[str, Any]],
        characters: List[Dict[str, Any]],
        knowledge_index: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        导出完整故事书
        """
        storybook = {
            "title": title,
            "subtitle": subtitle,
            "generated_at": datetime.now().isoformat(),
            "chapters": chapters,
            "characters": characters,
            "knowledge_index": knowledge_index,
            "total_chapters": len(chapters),
            "total_pages": sum(c["total_pages"] for c in chapters)
        }
        
        # 导出JSON
        json_path = os.path.join(self.output_dir, "storybook.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(storybook, f, ensure_ascii=False, indent=2)
        
        # 导出Markdown
        md_path = os.path.join(self.output_dir, "storybook.md")
        self._export_to_markdown(storybook, md_path)
        
        return {
            "json": json_path,
            "markdown": md_path
        }
    
    def _export_to_markdown(self, storybook: Dict, output_path: str):
        """导出为Markdown格式"""
        lines = [
            f"# {storybook['title']}",
            "",
            f"**副标题**: {storybook['subtitle']}",
            f"**生成时间**: {storybook['generated_at']}",
            "",
            "---",
            "",
            "## 目录",
            ""
        ]
        
        for chapter in storybook["chapters"]:
            lines.append(f"- 第{chapter['chapter_number']}章：{chapter['chapter_title']}")
        
        lines.append("")
        lines.append("---")
        
        for chapter in storybook["chapters"]:
            lines.append("")
            lines.append(f"# 第{chapter['chapter_number']}章：{chapter['chapter_title']}")
            lines.append("")
            
            for page in chapter["pages"]:
                lines.append(f"### 第{page['page_number']}页：{page['title']}")
                lines.append("")
                lines.append(page["content"])
                lines.append("")
                lines.append(f"*[阅读时间]: {page['reading_time']}")
                lines.append(f"*[插图提示]: {page['illustration_prompt']}")
                
                if page.get("knowledge_notes"):
                    lines.append("")
                    lines.append("**知识点**:")
                    for note in page["knowledge_notes"]:
                        lines.append(f"- {note}")
                
                lines.append("")
                lines.append("---")
        
        lines.append("")
        lines.append("## 知识索引")
        lines.append("")
        
        for topic, points in storybook["knowledge_index"].items():
            lines.append(f"### {topic}")
            for point in points:
                lines.append(f"- {point}")
            lines.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="1001夜童话故事汇 - 卡牌与故事书生成器")
    parser.add_argument("--type", type=str, default="card", choices=["card", "storybook"], help="生成类型")
    parser.add_argument("--output", type=str, default="./output", help="输出目录")
    parser.add_argument("--format", type=str, default="json", choices=["json", "markdown"], help="导出格式")
    
    args = parser.parse_args()
    
    if args.type == "card":
        generator = CardGameGenerator(output_dir=args.output)
        
        # 示例：生成知识点卡牌
        example_cards = [
            generator.generate_knowledge_card(
                knowledge_point="光合作用",
                knowledge_type="process",
                content="植物通过光合作用将阳光转化为能量，释放氧气",
                difficulty="medium",
                bonus_effect="答对可获得+20知识能量"
            ),
            generator.generate_knowledge_card(
                knowledge_point="勾股定理",
                knowledge_type="concept",
                content="直角三角形两直角边的平方和等于斜边的平方",
                difficulty="hard",
                bonus_effect="答对可解锁几何魔法"
            ),
            generator.generate_character_card(
                name="小光",
                role="光合作用精灵",
                abilities=["阳光收集", "能量转化", "氧气释放"],
                story_background="来自阳光王国的精灵，掌管着生命之光的魔法",
                visual_features="绿色翅膀、发光的身体、头顶有太阳标志"
            )
        ]
        
        print("=" * 50)
        print("1001夜童话故事汇 - 卡牌生成示例")
        print("=" * 50)
        
        for card in example_cards:
            print(f"\n[卡牌] {card['name']}")
            print(f"  类型: {card.get('type', card.get('role'))}")
            print(f"  内容: {card.get('content', card.get('story_background', ''))[:50]}...")
        
        # 导出
        json_path = generator.export_to_json(example_cards, "knowledge_cards.json")
        md_path = generator.export_to_markdown(example_cards, "knowledge_cards.md")
        
        print(f"\n[成功] 导出卡牌到:")
        print(f"  - JSON: {json_path}")
        print(f"  - Markdown: {md_path}")
    
    else:
        generator = StoryBookGenerator(output_dir=args.output)
        
        # 示例：生成故事书
        example_pages = [
            generator.generate_story_page(
                page_number=1,
                title="森林里的秘密",
                content="在一片神奇的森林里，住着一只会发光的萤火虫，名叫小光...",
                illustration_prompt="童话风格插图，发光的萤火虫在夜晚的魔法森林中飞翔，星星和月亮照耀",
                knowledge_notes=["萤火虫为什么会发光？"]
            )
        ]
        
        example_chapters = [
            generator.generate_story_chapter(
                chapter_number=1,
                chapter_title="光明的起源",
                pages=example_pages,
                knowledge_summary=["生物发光现象", "萤火虫的生命周期"]
            )
        ]
        
        paths = generator.export_storybook(
            title="1001夜知识童话：第一集",
            subtitle="用故事学习科学知识",
            chapters=example_chapters,
            characters=[
                {"name": "小光", "role": "萤火虫精灵", "description": "会发光的神奇萤火虫"}
            ],
            knowledge_index={
                "生物科学": ["萤火虫发光原理"],
                "自然科学": ["生物发光现象"]
            }
        )
        
        print("=" * 50)
        print("1001夜童话故事汇 - 故事书生成示例")
        print("=" * 50)
        
        print(f"\n[成功] 导出故事书到:")
        for format_type, path in paths.items():
            print(f"  - {format_type}: {path}")


if __name__ == "__main__":
    main()
