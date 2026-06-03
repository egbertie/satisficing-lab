#!/usr/bin/env python3
"""
Valid Skill - Main Entry Point
"""

import argparse
import yaml
import sys


def load_config():
    """加载配置"""
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Valid Skill Example"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 1.0.0"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="配置文件路径"
    )
    
    args = parser.parse_args()
    
    config = load_config()
    print(f"Skill: {config['skill']['name']}")
    print(f"Version: {config['skill']['version']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
