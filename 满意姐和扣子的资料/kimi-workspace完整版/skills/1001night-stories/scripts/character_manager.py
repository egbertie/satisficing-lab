#!/usr/bin/env python3
"""
1001夜童话故事汇 - 角色一致性管理器
维护角色档案，确保多场景/多故事中角色外观和性格一致
"""

import os
import json
import argparse
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime


class CharacterProfile:
    """角色档案类"""
    
    def __init__(
        self,
        name: str,
        role_type: str,
        visual_features: Dict[str, str],
        personality: List[str],
        color_palette: Dict[str, str],
        voice_description: str = "",
        backstory: str = ""
    ):
        self.name = name
        self.role_type = role_type  # protagonist/antagonist/helper/mascot
        self.visual_features = visual_features
        self.personality = personality
        self.color_palette = color_palette
        self.voice_description = voice_description
        self.backstory = backstory
        self.variations = []  # 场景变体
        self.version = 1
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "role_type": self.role_type,
            "visual_features": self.visual_features,
            "personality": self.personality,
            "color_palette": self.color_palette,
            "voice_description": self.voice_description,
            "backstory": self.backstory,
            "variations": self.variations,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CharacterProfile":
        """从字典创建"""
        profile = cls(
            name=data["name"],
            role_type=data["role_type"],
            visual_features=data["visual_features"],
            personality=data["personality"],
            color_palette=data["color_palette"],
            voice_description=data.get("voice_description", ""),
            backstory=data.get("backstory", "")
        )
        profile.variations = data.get("variations", [])
        profile.version = data.get("version", 1)
        profile.created_at = data.get("created_at", datetime.now().isoformat())
        profile.updated_at = data.get("updated_at", datetime.now().isoformat())
        return profile
    
    def add_variation(self, scene: str, appearance_modifier: str):
        """添加场景变体"""
        self.variations.append({
            "scene": scene,
            "appearance_modifier": appearance_modifier,
            "added_at": datetime.now().isoformat()
        })
        self.updated_at = datetime.now().isoformat()
    
    def generate_consistency_prompt(self, scene: str = "") -> str:
        """生成一致性prompt"""
        # 基础特征描述
        features_desc = []
        for feature_type, description in self.visual_features.items():
            features_desc.append(f"{feature_type}: {description}")
        
        # 配色方案
        color_desc = ", ".join([f"{k}: {v}" for k, v in self.color_palette.items()])
        
        # 查找场景变体
        modifier = ""
        for variation in self.variations:
            if variation["scene"] in scene:
                modifier = variation["appearance_modifier"]
                break
        
        # 构建完整prompt
        prompt_parts = [
            f"角色名: {self.name}",
            f"角色类型: {self.role_type}",
            f"外观特征: {'; '.join(features_desc)}",
            f"配色方案: {color_desc}",
            f"性格特点: {', '.join(self.personality)}"
        ]
        
        if modifier:
            prompt_parts.append(f"场景适配: {modifier}")
        
        if scene:
            prompt_parts.append(f"当前场景: {scene}")
        
        return "，".join(prompt_parts)


class CharacterManager:
    """角色管理器"""
    
    def __init__(self, data_dir: str = "./character_data"):
        self.data_dir = data_dir
        self.characters: Dict[str, CharacterProfile] = {}
        self.ensure_data_dir()
        self.load_all()
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_profile_path(self, name: str) -> str:
        """获取角色档案路径"""
        safe_name = name.lower().replace(" ", "_")
        return os.path.join(self.data_dir, f"{safe_name}.json")
    
    def create_character(
        self,
        name: str,
        role_type: str,
        visual_features: Dict[str, str],
        personality: List[str],
        color_palette: Dict[str, str],
        voice_description: str = "",
        backstory: str = ""
    ) -> CharacterProfile:
        """创建新角色"""
        profile = CharacterProfile(
            name=name,
            role_type=role_type,
            visual_features=visual_features,
            personality=personality,
            color_palette=color_palette,
            voice_description=voice_description,
            backstory=backstory
        )
        
        self.characters[name] = profile
        self.save_profile(name)
        
        return profile
    
    def get_character(self, name: str) -> Optional[CharacterProfile]:
        """获取角色"""
        return self.characters.get(name)
    
    def save_profile(self, name: str) -> str:
        """保存角色档案"""
        profile = self.characters.get(name)
        if not profile:
            raise ValueError(f"角色 {name} 不存在")
        
        path = self._get_profile_path(name)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)
        
        return path
    
    def load_profile(self, name: str) -> Optional[CharacterProfile]:
        """加载单个角色档案"""
        path = self._get_profile_path(name)
        if not os.path.exists(path):
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        profile = CharacterProfile.from_dict(data)
        self.characters[name] = profile
        return profile
    
    def load_all(self):
        """加载所有角色档案"""
        if not os.path.exists(self.data_dir):
            return
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                name = filename[:-5].replace("_", " ")
                self.load_profile(name)
    
    def list_characters(self) -> List[Dict[str, Any]]:
        """列出所有角色"""
        return [
            {
                "name": p.name,
                "role_type": p.role_type,
                "version": p.version,
                "updated_at": p.updated_at
            }
            for p in self.characters.values()
        ]
    
    def update_character(
        self,
        name: str,
        **kwargs
    ) -> Optional[CharacterProfile]:
        """更新角色"""
        profile = self.characters.get(name)
        if not profile:
            return None
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.version += 1
        profile.updated_at = datetime.now().isoformat()
        
        self.save_profile(name)
        return profile
    
    def add_scene_variation(
        self,
        character_name: str,
        scene: str,
        appearance_modifier: str
    ) -> bool:
        """为角色添加场景变体"""
        profile = self.characters.get(character_name)
        if not profile:
            return False
        
        profile.add_variation(scene, appearance_modifier)
        profile.version += 1
        profile.updated_at = datetime.now().isoformat()
        
        self.save_profile(character_name)
        return True
    
    def generate_consistency_prompt(
        self,
        character_name: str,
        scene: str = ""
    ) -> Optional[str]:
        """生成角色一致性prompt"""
        profile = self.characters.get(character_name)
        if not profile:
            return None
        
        return profile.generate_consistency_prompt(scene)
    
    def export_all(self) -> Dict[str, str]:
        """导出所有角色为JSON"""
        output = {
            "exported_at": datetime.now().isoformat(),
            "total_characters": len(self.characters),
            "characters": {
                name: profile.to_dict()
                for name, profile in self.characters.items()
            }
        }
        
        path = os.path.join(self.data_dir, "all_characters.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        return {"path": path, "data": output}


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="1001夜童话故事汇 - 角色一致性管理器")
    parser.add_argument("--action", type=str, default="list", 
                       choices=["list", "create", "get", "update", "variation", "prompt", "export"],
                       help="操作类型")
    parser.add_argument("--name", type=str, help="角色名称")
    parser.add_argument("--role", type=str, help="角色类型")
    parser.add_argument("--data-dir", type=str, default="./character_data", help="数据目录")
    
    args = parser.parse_args()
    manager = CharacterManager(data_dir=args.data_dir)
    
    if args.action == "list":
        print("=" * 50)
        print("角色列表")
        print("=" * 50)
        characters = manager.list_characters()
        if not characters:
            print("暂无角色")
        else:
            for char in characters:
                print(f"\n[角色] {char['name']}")
                print(f"  类型: {char['role_type']}")
                print(f"  版本: {char['version']}")
                print(f"  更新时间: {char['updated_at']}")
    
    elif args.action == "create":
        if not args.name or not args.role:
            print("错误: 创建角色需要 --name 和 --role 参数")
            return
        
        # 交互式创建（简化版）
        profile = manager.create_character(
            name=args.name,
            role_type=args.role,
            visual_features={
                "发型": "待补充",
                "服装": "待补充",
                "配饰": "待补充"
            },
            personality=["友善", "勇敢"],
            color_palette={
                "主色": "待补充",
                "辅色": "待补充",
                "强调色": "待补充"
            },
            backstory=f"{args.name}是一个神秘的角色"
        )
        
        print(f"[成功] 创建角色: {profile.name}")
        print(f"档案路径: {manager._get_profile_path(profile.name)}")
    
    elif args.action == "get":
        if not args.name:
            print("错误: 获取角色需要 --name 参数")
            return
        
        profile = manager.get_character(args.name)
        if profile:
            print(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"角色 {args.name} 不存在")
    
    elif args.action == "prompt":
        if not args.name:
            print("错误: 生成prompt需要 --name 参数")
            return
        
        prompt = manager.generate_consistency_prompt(args.name, "")
        if prompt:
            print("=" * 50)
            print(f"角色一致性Prompt - {args.name}")
            print("=" * 50)
            print(prompt)
        else:
            print(f"角色 {args.name} 不存在")
    
    elif args.action == "export":
        result = manager.export_all()
        print(f"[成功] 导出所有角色到: {result['path']}")
        print(f"角色总数: {result['data']['total_characters']}")
    
    else:
        print("使用 --help 查看帮助")


if __name__ == "__main__":
    main()
