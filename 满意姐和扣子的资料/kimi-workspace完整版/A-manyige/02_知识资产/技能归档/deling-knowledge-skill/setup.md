# Setup Guide - 德灵 MCP Skill

> 本文档描述配置步骤，AI Agent 应读取后自动完成配置。

## 前置条件

用户需要提供以下两个参数：

| 参数              | 说明        |
| ----------------- | ----------- |
| `X-Access-Key-Id` | 访问密钥 ID |
| `X-Authorization` | 授权令牌    |

## 配置步骤

### Step 1: 检查 mcporter 是否已安装

运行以下命令检查 mcporter 是否已安装：

```bash
mcporter --version
```

如果命令执行成功并显示版本号，说明已安装，跳过下一步。

### Step 2: 安装 mcporter（若未安装）

若上一步检查失败（提示命令未找到），则执行以下命令进行安装：

```bash
npm install -g mcporter
```

> **注**：若安装失败（提示 `npm` 命令未找到），说明未安装 Node.js，请先安装 Node.js（https://nodejs.org/），然后重试。

安装完成后，再次运行 `mcporter --version` 验证安装是否成功。

### Step 3: 获取用户参数

确认用户是否已提供 `X-Access-Key-Id` 和 `X-Authorization`。如果用户未提供，向用户询问。

**校验规则**：两个参数均不能为空。

### Step 4: 确定配置文件路径

配置文件路径为：

| 操作系统      | 路径                                        |
| ------------- | ------------------------------------------- |
| macOS / Linux | `~/.mcporter/mcporter.json`                 |
| Windows       | `%USERPROFILE%\.mcporter\mcporter.json`     |
| WSL           | `~/.mcporter/mcporter.json`（Linux 侧路径） |

### Step 5: 写入配置

1. 如果 `.mcporter` 目录不存在，创建它
2. 如果 `mcporter.json` 配置文件不存在，将以下 JSON 写入配置文件（替换 `{X-Access-Key-Id}` 和 `{X-Authorization}` 为用户提供的实际值）：

```json
{
  "mcpServers": {
    "deling": {
      "url": "{url}",
      "transportType": "streamable-http",
      "headers": {
        "X-Access-Key-Id": "{X-Access-Key-Id}",
        "X-Authorization": "{X-Authorization}"
      }
    }
  }
}
```

3. 如果 `mcporter.json` 配置文件已存在，先读取已有配置，再将 deling 条目与已有配置一并写入（合并而非覆盖整个文件）

   **合并示例**：假设现有配置为：

   ```json
   {
     "mcpServers": {
       "existing-service": {
         "url": "https://existing.example.com",
         "transportType": "streamable-http"
       }
     }
   }
   ```

   合并后应为：

   ```json
   {
     "mcpServers": {
       "existing-service": {
         "url": "https://existing.example.com",
         "transportType": "streamable-http"
       },
       "deling": {
         "url": "{url}",
         "transportType": "streamable-http",
         "headers": {
           "X-Access-Key-Id": "{X-Access-Key-Id}",
           "X-Authorization": "{X-Authorization}"
         }
       }
     }
   }
   ```

**编码要求**：

- 文件必须以 UTF-8 无 BOM 编码保存
- JSON 使用 2 空格缩进，保持紧凑格式

### Step 6: 确认结果

配置写入后，告知用户配置文件的完整路径，并提示配置完成。

### Step 7: 验证安装

运行以下命令验证安装是否成功：

```bash
mcporter call deling.sessions_search question="测试" top_n=1 --output raw
```

如果返回正常结果（无错误信息），说明配置成功。

## 注意事项

- 不要在输出中回显 `X-Access-Key-Id` 和 `X-Authorization` 的完整值（安全考虑）
- 如果已有`mcporter.json`配置文件且其包含其他 mcpServers 条目，应合并而非覆盖整个文件
- Windows 环境下注意路径分隔符使用 `\`
