#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ResearchPro 技能打包脚本

将技能文件打包成 ZIP，准备上传到腾讯 SkillHub
"""

import os
import zipfile
from pathlib import Path
from datetime import datetime


def package_skill():
    """打包技能文件"""
    
    # 获取当前目录
    skill_dir = Path(__file__).parent
    output_dir = skill_dir.parent
    
    # 定义需要打包的文件
    files_to_include = [
        "main.py",
        "SKILL.md",
        "README.md",
        "API_KEY_GUIDE.md",
        "requirements.txt",
        "test_connection.py",
    ]
    
    # 生成压缩包名称
    version = "v1.0.0"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"ResearchPro_{version}_{timestamp}.zip"
    zip_path = output_dir / zip_name
    
    # 创建 ZIP 文件
    print(f"\n📦 开始打包 ResearchPro 技能...\n")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name in files_to_include:
            file_path = skill_dir / file_name
            
            if file_path.exists():
                # 计算在 ZIP 中的相对路径
                arc_name = f"researchpro/{file_name}"
                zipf.write(file_path, arcname=arc_name)
                
                file_size = file_path.stat().st_size
                print(f"  ✓ {file_name:25} ({file_size:,} bytes)")
            else:
                print(f"  ⚠️  {file_name} (未找到，跳过)")
    
    # 显示打包结果
    zip_size = zip_path.stat().st_size
    
    print(f"\n✅ 打包完成!")
    print(f"\n压缩包信息:")
    print(f"  文件名：{zip_name}")
    print(f"  大小：{zip_size:,} bytes ({zip_size/1024:.2f} KB)")
    print(f"  位置：{zip_path}\n")
    
    # 检查是否超过 SkillHub 限制（10MB）
    size_limit = 10 * 1024 * 1024  # 10MB
    if zip_size > size_limit:
        print("⚠️  警告：压缩包超过 10MB，可能无法上传到 SkillHub")
        print("建议:")
        print("  - 移除不必要的大文件")
        print("  - 压缩图片资源")
        print("  - 拆分技能包\n")
    else:
        remaining = size_limit - zip_size
        print(f"✓ 符合 SkillHub 要求（剩余空间：{remaining/1024:.2f} KB）\n")
    
    # 下一步指引
    print("=" * 60)
    print("【下一步】上传到腾讯 SkillHub")
    print("=" * 60)
    print("\n步骤:")
    print("  1. 登录 https://open.dingtalk.com/skillhub (或对应平台)")
    print("  2. 点击 '创建新技能'")
    print("  3. 上传 ZIP 文件")
    print("  4. 填写技能描述和元数据")
    print("  5. 提交审核（1-3 个工作日）\n")
    
    print("💡 提示:")
    print("  - SKILL.md 已包含完整的技能说明")
    print("  - README.md 可作为用户文档链接")
    print("  - API_KEY_GUIDE.md 帮助用户配置密钥\n")


if __name__ == "__main__":
    package_skill()
