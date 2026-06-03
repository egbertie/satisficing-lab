#!/bin/bash
# 对抗测试运行脚本

cd "$(dirname "$0")"

python3 adversarial_tests.py "$@"
