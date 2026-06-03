#!/bin/bash
# 安全审计修复脚本

echo "=== OpenClaw 安全加固脚本 ==="

# 1. 备份配置
echo "[1/3] 备份当前配置..."
cp /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.backup.$(date +%Y%m%d_%H%M%S)
echo "✓ 配置已备份"

# 2. 应用配置补丁
echo "[2/3] 应用安全加固配置..."
python3 << 'PYEOF'
import json

config_file = "/root/.openclaw/openclaw.json"

with open(config_file, 'r') as f:
    config = json.load(f)

# 修复1: 添加 trustedProxies
if 'gateway' not in config:
    config['gateway'] = {}
config['gateway']['trustedProxies'] = ["127.0.0.1", "::1"]

# 修复2: 设置插件白名单
if 'plugins' not in config:
    config['plugins'] = {}
config['plugins']['allow'] = [
    "@m1heng-clawd/feishu",
    "@wecom/wecom-openclaw-plugin",
    "dingtalk-moltbot-connector",
    "kimi-claw"
]

# 修复3: 调整工具策略
if 'tools' not in config:
    config['tools'] = {}
config['tools']['profile'] = "minimal"

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("✓ 配置已更新:")
print("  - gateway.trustedProxies: 已设置")
print("  - plugins.allow: 已设置白名单")
print("  - tools.profile: 已改为minimal")
PYEOF

echo "✓ 配置补丁应用成功"

# 3. 创建信任声明
echo "[3/3] 创建插件信任声明..."
python3 << 'PYEOF'
content = '''# 可信插件声明

## 已安装插件信任声明

以下插件是用户主动安装的可信来源插件：

- @m1heng-clawd/feishu (npm官方, 飞书业务集成)
- @wecom/wecom-openclaw-plugin (npm官方, 企业微信业务集成)
- dingtalk-moltbot-connector (GitHub, 钉钉业务集成)
- kimi-claw (本地路径, Kimi核心通道)

## 风险接受声明

上述插件的代码模式警告已审查并接受风险。

## 审查记录

- 首次审查: 2026-03-22
- 下次审查: 2026-04-22
'''

with open('/root/.openclaw/workspace/docs/TRUSTED_PLUGINS.md', 'w') as f:
    f.write(content)
print("✓ 信任声明已创建")
PYEOF

echo ""
echo "=== 安全加固完成 ==="
echo "建议: 运行 'openclaw gateway restart' 重启服务"
