#!/usr/bin/env python3
"""
1001夜童话故事汇 - 万相2.7图像生成器
支持文生图、文生组图、图生图、图像编辑等功能
"""

import os
import json
import base64
import time
import argparse
from typing import Optional, Dict, Any, List
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# 万相2.7 API配置
WANX_API_URL = "https://api.alipan.com/v1/images/generations"
MODEL_NAME = "wanx2.7-image-generator"


class Wanx27ImageGenerator:
    """万相2.7图像生成器"""
    
    def __init__(self, api_keys: List[str], output_dir: str = "./output"):
        """
        初始化生成器
        
        Args:
            api_keys: API密钥列表
            output_dir: 输出目录
        """
        self.api_keys = api_keys
        self.current_key_index = 0
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_current_key(self) -> str:
        """获取当前API密钥"""
        return self.api_keys[self.current_key_index]
    
    def _rotate_key(self):
        """轮换到下一个API密钥"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
    
    def _call_api(self, payload: Dict) -> Dict:
        """调用万相2.7 API"""
        api_key = self._get_current_key()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            req = Request(
                WANX_API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            
            with urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result
                
        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            raise Exception(f"API调用失败 [{e.code}]: {error_body}")
        except URLError as e:
            raise Exception(f"网络错误: {str(e)}")
    
    def text_to_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        size: str = "1024*1024",
        n: int = 1,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        文生图 - 根据文本描述生成图像
        
        Args:
            prompt: 图像描述（正向提示词）
            negative_prompt: 负面提示词（需要避免的元素）
            size: 图像尺寸，支持 1024*1024, 720*1280, 1280*720
            n: 生成数量（1-4）
            seed: 随机种子（可选）
        
        Returns:
            生成结果列表
        """
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "negative_prompt": negative_prompt or "低质量, 模糊, 畸形, 错误比例",
            "size": size,
            "n": min(n, 4),
            "seed": seed if seed else -1
        }
        
        print(f"[Wanx27] 文生图模式")
        print(f"[Wanx27] Prompt: {prompt[:100]}...")
        
        result = self._call_api(payload)
        
        return self._process_result(result, "text2img")
    
    def text_to_image_group(
        self,
        prompts: List[str],
        size: str = "1024*1024",
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        文生组图 - 一次性生成多张相关图像
        
        Args:
            prompts: 多个图像描述列表
            size: 图像尺寸
            seed: 随机种子（可选）
        
        Returns:
            生成结果列表
        """
        payload = {
            "model": MODEL_NAME,
            "prompt": prompts,
            "size": size,
            "n": len(prompts),
            "seed": seed if seed else -1
        }
        
        print(f"[Wanx27] 文生组图模式 - {len(prompts)}张图")
        
        result = self._call_api(payload)
        
        return self._process_result(result, "text2img_group")
    
    def image_to_image(
        self,
        prompt: str,
        input_image: str,
        negative_prompt: str = "",
        size: str = "1024*1024",
        similarity: float = 0.7,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        图生图 - 根据参考图生成新图像
        
        Args:
            prompt: 图像描述
            input_image: 参考图路径或URL
            negative_prompt: 负面提示词
            size: 图像尺寸
            similarity: 与参考图的相似度 (0-1)
            seed: 随机种子（可选）
        
        Returns:
            生成结果列表
        """
        # 读取并编码参考图
        image_data = self._load_image_base64(input_image)
        
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "negative_prompt": negative_prompt or "低质量, 模糊, 畸形, 错误比例",
            "input_image": image_data,
            "size": size,
            "similarity": similarity,
            "n": 1,
            "seed": seed if seed else -1
        }
        
        print(f"[Wanx27] 图生图模式")
        print(f"[Wanx27] 参考图: {input_image}")
        print(f"[Wanx27] Prompt: {prompt[:100]}...")
        
        result = self._call_api(payload)
        
        return self._process_result(result, "img2img")
    
    def image_edit(
        self,
        prompt: str,
        input_image: str,
        mask_image: Optional[str] = None,
        negative_prompt: str = "",
        size: str = "1024*1024",
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        图像编辑 - 修改图像指定区域
        
        Args:
            prompt: 编辑描述
            input_image: 原图路径
            mask_image: 蒙版图路径（白色区域将被编辑）
            negative_prompt: 负面提示词
            size: 图像尺寸
            seed: 随机种子（可选）
        
        Returns:
            生成结果列表
        """
        image_data = self._load_image_base64(input_image)
        
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "negative_prompt": negative_prompt or "低质量, 模糊, 畸形",
            "input_image": image_data,
            "size": size,
            "n": 1,
            "seed": seed if seed else -1
        }
        
        if mask_image:
            mask_data = self._load_image_base64(mask_image)
            payload["mask_image"] = mask_data
        
        print(f"[Wanx27] 图像编辑模式")
        print(f"[Wanx27] Prompt: {prompt[:100]}...")
        
        result = self._call_api(payload)
        
        return self._process_result(result, "edit")
    
    def multi_reference_generation(
        self,
        prompts: List[str],
        reference_images: List[str],
        similarity: float = 0.6,
        size: str = "1024*1024"
    ) -> List[Dict[str, Any]]:
        """
        多图参考生成 - 基于多张参考图生成新图
        
        Args:
            prompts: 图像描述列表
            reference_images: 参考图路径列表
            similarity: 相似度
            size: 图像尺寸
        
        Returns:
            生成结果列表
        """
        ref_images = [self._load_image_base64(img) for img in reference_images]
        
        payload = {
            "model": MODEL_NAME,
            "prompt": prompts,
            "reference_image": ref_images,
            "similarity": similarity,
            "size": size,
            "n": len(prompts)
        }
        
        print(f"[Wanx27] 多图参考生成 - {len(reference_images)}张参考图")
        
        result = self._call_api(payload)
        
        return self._process_result(result, "multi_ref")
    
    def interactive_edit(
        self,
        prompt: str,
        input_image: str,
        edit_type: str = "style",
        size: str = "1024*1024",
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        交互式编辑 - 风格转换、局部重绘等
        
        Args:
            prompt: 编辑指令
            input_image: 输入图路径
            edit_type: 编辑类型 (style/color/object/removal)
            size: 图像尺寸
            seed: 随机种子（可选）
        
        Returns:
            生成结果列表
        """
        image_data = self._load_image_base64(input_image)
        
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "input_image": image_data,
            "edit_type": edit_type,
            "size": size,
            "n": 1,
            "seed": seed if seed else -1
        }
        
        print(f"[Wanx27] 交互式编辑 - 类型: {edit_type}")
        
        result = self._call_api(payload)
        
        return self._process_result(result, "interactive")
    
    def _load_image_base64(self, image_path: str) -> str:
        """加载图片并转为base64"""
        if image_path.startswith("http"):
            with urlopen(image_path) as response:
                data = response.read()
        else:
            with open(image_path, "rb") as f:
                data = f.read()
        
        return base64.b64encode(data).decode("utf-8")
    
    def _process_result(self, result: Dict, mode: str) -> List[Dict[str, Any]]:
        """处理API返回结果"""
        outputs = []
        
        if "data" in result:
            for idx, item in enumerate(result["data"]):
                output_item = {
                    "mode": mode,
                    "url": item.get("url", ""),
                    "b64_json": item.get("b64_json", ""),
                    "revised_prompt": item.get("revised_prompt", ""),
                    "index": idx
                }
                
                # 保存图像
                if item.get("url"):
                    output_item["local_path"] = self._download_image(
                        item["url"], f"{mode}_{idx}"
                    )
                
                outputs.append(output_item)
        
        print(f"[Wanx27] 生成完成: {len(outputs)}张图像")
        return outputs
    
    def _download_image(self, url: str, prefix: str) -> str:
        """下载并保存图像"""
        timestamp = int(time.time())
        filename = f"{prefix}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with urlopen(url, timeout=60) as response:
                data = response.read()
                with open(filepath, "wb") as f:
                    f.write(data)
                print(f"[Wanx27] 保存图像: {filepath}")
        except Exception as e:
            print(f"[Wanx27] 下载失败: {e}")
            filepath = ""
        
        return filepath
    
    def generate_story_illustration(
        self,
        prompt: str,
        character_prompt: str = "",
        scene: str = "",
        style: str = "童话绘本",
        age_group: str = "儿童",
        size: str = "1024*1024",
        overlay_text: str = ""
    ) -> Dict[str, Any]:
        """
        生成故事插图的便捷方法
        
        Args:
            prompt: 场景描述
            character_prompt: 角色描述
            scene: 场景环境
            style: 艺术风格
            age_group: 目标年龄组
            size: 图像尺寸
            overlay_text: 画面中需要包含的文字内容（如标题、标签等）
        
        Returns:
            生成结果
        """
        # 构建完整prompt
        full_prompt = self._build_story_prompt(
            prompt, character_prompt, scene, style, age_group, overlay_text
        )
        
        # 选择合适的负面提示词
        negative = self._get_age_appropriate_negative(age_group)
        
        return self.text_to_image(
            prompt=full_prompt,
            negative_prompt=negative,
            size=size
        )[0]
    
    def generate_card_image(
        self,
        card_name: str,
        card_type: str,
        description: str,
        stats: Dict[str, Any] = None,
        style: str = "童话卡牌",
        size: str = "1024*1024"
    ) -> Dict[str, Any]:
        """
        生成知识卡牌图片（包含画面文字）
        
        Args:
            card_name: 卡牌名称
            card_type: 卡牌类型 (hero/skill/scene/gem)
            description: 卡牌描述/知识内容
            stats: 卡牌属性数值 {"atk": 100, "def": 80, "skill": "技能名"}
            style: 艺术风格
            size: 图像尺寸
        
        Returns:
            生成结果
        
        Example:
            generator.generate_card_image(
                card_name="光之勇者",
                card_type="hero",
                description="太阳之心的守护者",
                stats={"atk": 100, "def": 80, "skill": "光芒万丈"}
            )
        """
        # 构建卡牌视觉描述
        type_icons = {
            "hero": "勇敢的战士",
            "skill": "魔法技能",
            "scene": "神秘场景",
            "gem": "知识宝石"
        }
        type_desc = type_icons.get(card_type, "神秘卡牌")
        
        # 构建画面文字
        stats_text = ""
        if stats:
            stat_parts = []
            if "atk" in stats:
                stat_parts.append(f"ATK:{stats['atk']}")
            if "def" in stats:
                stat_parts.append(f"DEF:{stats['def']}")
            if "skill" in stats:
                stat_parts.append(f"技能:{stats['skill']}")
            if "value" in stats:
                stat_parts.append(f"价值:{stats['value']}")
            stats_text = " ".join(stat_parts)
        
        # 组合画面中的文字内容
        card_text_elements = [
            f"卡牌名:{card_name}",
            f"类型:{type_desc}",
            description,
            stats_text
        ]
        overlay_text = " | ".join([t for t in card_text_elements if t])
        
        # 构建完整prompt
        prompt = f"""
        {type_desc}卡牌设计，中心是{card_name}的精美插图，
        卡牌边缘有装饰性边框，背景有{type_desc}主题图案，
        包含清晰可见的文字标签: "{overlay_text}"
        魔法卡牌风格，华丽边框，金色装饰
        """
        
        return self.text_to_image(
            prompt=prompt.strip(),
            negative_prompt="低质量, 模糊, 畸形, 错误文字, 乱码文字",
            size=size
        )[0]
    
    def generate_knowledge_card(
        self,
        title: str,
        knowledge_content: str,
        visual_element: str = "",
        style: str = "知识卡片",
        size: str = "1024*1024"
    ) -> Dict[str, Any]:
        """
        生成知识卡片图片（包含知识点文字）
        
        Args:
            title: 卡片标题
            knowledge_content: 知识内容/公式/定义
            visual_element: 视觉元素描述
            style: 艺术风格
            size: 图像尺寸
        
        Returns:
            生成结果
        
        Example:
            generator.generate_knowledge_card(
                title="水的奥秘",
                knowledge_content="H₂O = 2个氢 + 1个氧",
                visual_element="水分子结构图"
            )
        """
        prompt = f"""
        知识卡片设计，主题是{title}，
        卡片中心有清晰的{visual_element or "相关插图"}，
        包含文字标签: "【{title}】" 和 "{knowledge_content}"，
        背景有学习氛围的元素（书本、星星、魔法光芒），
        知识科普风格，清晰易读，色彩温暖
        """
        
        return self.text_to_image(
            prompt=prompt.strip(),
            negative_prompt="低质量, 模糊, 错误文字, 乱码",
            size=size
        )[0]
    
    def generate_scene_with_label(
        self,
        scene_name: str,
        location_type: str,
        description: str = "",
        style: str = "童话场景",
        size: str = "1024*1024"
    ) -> Dict[str, Any]:
        """
        生成带地点标签的场景图片
        
        Args:
            scene_name: 场景/地点名称
            location_type: 地点类型 (island/forest/tower/temple/valley)
            description: 场景描述
            style: 艺术风格
            size: 图像尺寸
        
        Returns:
            生成结果
        
        Example:
            generator.generate_scene_with_label(
                scene_name="元素火山群岛",
                location_type="island",
                description="化学元素的家园"
            )
        """
        location_labels = {
            "island": "群岛·硫磺镇",
            "forest": "森林·迷宫入口",
            "tower": "塔楼·观星台",
            "temple": "圣殿·荣耀大厅",
            "valley": "山谷·彩虹之源"
        }
        label = location_labels.get(location_type, "神秘之地")
        
        prompt = f"""
        童话故事场景，{scene_name}的精美插图，
        场景中有明显的位置标识牌: "📍 {scene_name}·{label}"，
        包含{location_type}类型的典型元素，
        {description}，氛围感强，细节丰富
        """
        
        return self.text_to_image(
            prompt=prompt.strip(),
            negative_prompt="低质量, 模糊, 畸形",
            size=size
        )[0]
    
    def _build_story_prompt(
        self,
        prompt: str,
        character: str,
        scene: str,
        style: str,
        age_group: str,
        overlay_text: str = ""
    ) -> str:
        """构建故事风格的prompt"""
        style_descriptions = {
            "婴儿": "极简黑白插画, 简单几何形状, 高对比度",
            "幼儿": "可爱卡通风格, 明亮色彩, 圆润线条",
            "学龄前": "童趣插画, 温暖色调, 简单场景",
            "儿童": "童话绘本风格, 细腻画风, 丰富细节",
            "少年": "精美插画, 艺术感强, 故事性强",
            "青少年": "成熟插画, 构图精美, 氛围感",
            "成人": "专业艺术风格, 高品质, 深度表现"
        }
        
        style_suffix = style_descriptions.get(age_group, style_descriptions["儿童"])
        
        parts = [prompt]
        if character:
            parts.append(f"角色: {character}")
        if scene:
            parts.append(f"场景: {scene}")
        if overlay_text:
            parts.append(f"包含文字: \"{overlay_text}\"")
        parts.append(f"风格: {style_suffix}")
        
        return ", ".join(parts)
    
    def _get_age_appropriate_negative(self, age_group: str) -> str:
        """获取年龄适当的负面提示词"""
        base_negative = "低质量, 模糊, 畸形, 错误比例, 恐怖, 暴力"
        
        age_specific = {
            "婴儿": "复杂图案, 过多元素",
            "幼儿": "恐怖元素, 复杂场景",
            "学龄前": "恐怖内容, 暴力画面",
            "儿童": "血腥, 暴力, 色情",
            "少年": "",
            "青少年": "",
            "成人": ""
        }
        
        return f"{base_negative}, {age_specific.get(age_group, '')}"


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="1001夜童话故事汇 - 万相2.7图像生成器")
    parser.add_argument("--mode", type=str, default="text2img",
                       choices=["text2img", "img2img", "edit", "interactive", "story"],
                       help="生成模式")
    parser.add_argument("--prompt", type=str, help="图像描述")
    parser.add_argument("--prompts", type=str, help="多个描述（逗号分隔）")
    parser.add_argument("--image", type=str, help="参考图路径")
    parser.add_argument("--mask", type=str, help="蒙版图路径")
    parser.add_argument("--negative", type=str, default="", help="负面提示词")
    parser.add_argument("--size", type=str, default="1024*1024",
                       choices=["1024*1024", "720*1280", "1280*720"],
                       help="图像尺寸")
    parser.add_argument("--similarity", type=float, default=0.7, help="相似度")
    parser.add_argument("--output", type=str, default="./output", help="输出目录")
    parser.add_argument("--api-keys", type=str, help="API密钥（逗号分隔）")
    
    args = parser.parse_args()
    
    # API密钥
    api_keys_str = args.api_keys or os.environ.get("WANX_API_KEYS", "")
    if not api_keys_str:
        # 默认使用用户提供的密钥
        api_keys_str = "sk-02791f4e5ceb44ca99322e78c03e5ec1,sk-5ff36ee4460b4385a426e34db4d70b0d"
    
    api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
    
    generator = Wanx27ImageGenerator(api_keys=api_keys, output_dir=args.output)
    
    print("=" * 50)
    print("1001夜童话故事汇 - 万相2.7图像生成器")
    print("=" * 50)
    
    if args.mode == "text2img":
        if not args.prompt:
            print("错误: text2img模式需要 --prompt 参数")
            return
        
        result = generator.text_to_image(
            prompt=args.prompt,
            negative_prompt=args.negative,
            size=args.size
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.mode == "img2img":
        if not args.prompt or not args.image:
            print("错误: img2img模式需要 --prompt 和 --image 参数")
            return
        
        result = generator.image_to_image(
            prompt=args.prompt,
            input_image=args.image,
            negative_prompt=args.negative,
            similarity=args.similarity,
            size=args.size
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.mode == "edit":
        if not args.prompt or not args.image:
            print("错误: edit模式需要 --prompt 和 --image 参数")
            return
        
        result = generator.image_edit(
            prompt=args.prompt,
            input_image=args.image,
            mask_image=args.mask,
            negative_prompt=args.negative,
            size=args.size
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.mode == "interactive":
        if not args.prompt or not args.image:
            print("错误: interactive模式需要 --prompt 和 --image 参数")
            return
        
        result = generator.interactive_edit(
            prompt=args.prompt,
            input_image=args.image,
            size=args.size
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.mode == "story":
        if not args.prompt:
            print("错误: story模式需要 --prompt 参数")
            return
        
        result = generator.generate_story_illustration(
            prompt=args.prompt,
            size=args.size
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
