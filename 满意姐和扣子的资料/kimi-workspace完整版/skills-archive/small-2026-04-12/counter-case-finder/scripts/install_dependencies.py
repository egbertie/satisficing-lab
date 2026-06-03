#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装反向案例发现器技能所需的依赖
"""

import subprocess
import sys


def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
        print(f"[OK] 已安装: {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"[FAIL] 安装失败: {package}")
        return False


def main():
    print("正在安装反向案例发现器技能依赖...")
    print("-" * 50)
    
    packages = ["python-docx"]
    success_count = sum(1 for p in packages if install_package(p))
    
    print("-" * 50)
    print(f"安装完成: {success_count}/{len(packages)} 个包")
    
    if success_count == len(packages):
        print("[OK] 所有依赖安装成功！")
    else:
        print("[WARN] 部分依赖安装失败，请手动安装")


if __name__ == '__main__':
    main()
