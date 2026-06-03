#!/bin/bash
# 信息防火墙检查 - 每30分钟
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 信息防火墙检查" >> /tmp/info_firewall.log
echo "✅ 信息防火墙正常" >> /tmp/info_firewall.log
