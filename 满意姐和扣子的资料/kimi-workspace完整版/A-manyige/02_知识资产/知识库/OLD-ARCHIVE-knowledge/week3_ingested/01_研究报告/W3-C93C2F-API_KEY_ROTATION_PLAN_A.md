---
# 知识元数据 (5标准化)
knowledge_id: W3-C93C2F
title: API密钥轮换完整方案（方案A）
category: 01_研究报告
source: docs/API_KEY_ROTATION_PLAN_A.md
ingested_at: 2026-03-27 17:58:21
word_count: 3725
line_count: 233
week: 3
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# API密钥轮换完整方案（方案A）

> **知识ID**: W3-C93C2F  
> **分类**: 01_研究报告  
> **来源**: `docs/API_KEY_ROTATION_PLAN_A.md`  
> **入库时间**: 2026-03-27

## 摘要

> 准备时间：2026-03-21

---

## 正文

# API密钥轮换完整方案（方案A）
> 准备时间：2026-03-21
> 执行状态：待用户有空时执行
> 下周四提醒：2026-03-27 08:13

---

## 📋 轮换前准备清单

### 必须提前准备的
- [ ] 预留30-60分钟 uninterrupted time
- [ ] 确保能接收验证邮件/短信
- [ ] 备用网络环境（部分服务可能需海外IP）

---

## 🔑 当前API密钥清单

### 1. GitHub Token（最高优先级）
**当前状态**: 已泄露到Git历史
**文件位置**: `.config/github.env`
**用途**: 
- GitHub API调用
- GitHub Models (GPT-4o等)
- 代码推送/拉取

**重新获取步骤**:
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择有效期（建议90天）
4. 权限勾选：
   - ✅ repo (完整仓库访问)
   - ✅ workflow (Actions)
   - ✅ read:org (组织读取)
   - ✅ gist
5. 生成后立即复制（只显示一次）
6. 本地更新：`echo "GITHUB_TOKEN=ghp_xxxxx" > .config/github.env`

**特别注意**:
- 旧Token需手动撤销（在GitHub设置页面）
- 撤销后所有使用该Token的自动化将停止

---

### 2. Kimi API Key（月之暗面）
**当前状态**: 疑似泄露
**文件位置**: `.config/kimi.env`
**用途**:
- Kimi API调用
- 深度研究功能

**重新获取步骤**:
1. 访问 https://platform.moonshot.cn/
2. 登录账户
3. 进入 "API Key管理"
4. 点击 "新建"
5. 复制新Key
6. 本地更新：`echo "KIMI_API_KEY=sk-xxxxx" > .config/kimi.env`

**特别注意**:
- Kimi是包月制，新Key立即生效
- 旧Key可同时存在多个，无需立即删除

---

### 3. Jina AI API Key
**当前状态**: 疑似泄露
**文件位置**: `.config/jina.env`
**用途**:
- 网页内容提取
- 搜索增强

**重新获取步骤**:
1. 访问 https://jina.ai/
2. 点击右上角头像 → "API"
3. 或使用直接链接：https://jina.ai/api/
4. 生成新Key
5. 本地更新：`echo "JINA_API_KEY=jina_xxxxx" > .config/jina.env`

**特别注意**:
- 免费额度：1000次/天
- 旧Key可在控制台手动删除

---

### 4. Claude API Key（Anthropic）
**当前状态**: 疑似泄露，当前403错误
**文件位置**: `.config/claude.env`
**用途**:
- Claude API调用（备用模型）

**重新获取步骤**:
1. 访问 https://console.anthropic.com/
2. 登录账户
3. 进入 "API Keys"
4. 点击 "Create Key"
5. 复制新Key
6. 本地更新：`echo "ANTHROPIC_API_KEY=sk-ant-xxxxx" > .config/claude.env`

**特别注意**:
- 当前存在地区限制（403错误）
- 可能需要海外环境才能正常使用
- 建议先测试再完全切换

---

### 5. GitHub Models 专用Token
**当前状态**: 与GitHub Token共用，已泄露
**文件位置**: `.config/github_models.env`
**用途**:
- GitHub Models端点调用
- GPT-4o, Llama-3.1等模型

**重新获取步骤**:
与GitHub Token相同（复用同一个Token即可）

---

## 🧹 Git历史清理步骤（关键）

### 方案C（当前执行）：基础保护
已完成：`.env`文件权限收紧 + `.gitignore`更新

### 方案A（下周四执行）：完整清理

#### 步骤1：安装必要工具
```bash
# Ubuntu/Debian
sudo apt-get install git-filter-repo

# 或使用Python pip
pip install git-filter-repo
```

#### 步骤2：创建安全备份
```bash
# 备份当前仓库
cd /root/.openclaw/workspace
cp -r .git .git.backup.$(date +%Y%m%d)
```

#### 步骤3：执行Git历史清理
```bash
cd /root/.openclaw/workspace

# 清理.env文件历史
git filter-repo --path .env --invert-paths --force

# 清理config目录下所有.env
git filter-repo --path .config/claude.env --invert-paths --force
git filter-repo --path .config/github.env --invert-paths --force
git filter-repo --path .config/github_models.env --invert-paths --force
git filter-repo --path .config/jina.env --invert-paths --force
git filter-repo --path .config/kimi.env --invert-paths --force
```

#### 步骤4：强制推送（危险操作）
```bash
# 这会重写GitHub历史，协作者需重新clone
git push origin --force --all
git push origin --force --tags
```

#### 步骤5：验证清理结果
```bash
# 确认历史中无密钥
git log --all --full-history --oneline -- "*.env"
# 应返回空
```

---

## ⚠️ 风险提示

### 执行前必须知道
1. **Git历史重写后，所有协作者需重新clone仓库**
2. **如果仓库是public且已被fork，泄露的密钥可能已被他人保存**
3. **清理期间仓库将不可用（约5-15分钟）**

### 最低风险路径
如果担心操作风险，可以：
1. 仅轮换密钥（不清理Git历史）
2. 旧密钥在服务商处手动撤销
3. 接受Git历史中的密钥是"已失效"状态

---

## ✅ 执行检查清单

### 下周四执行时按此清单操作

#### 阶段1：密钥轮换（15分钟）
- [ ] 生成新GitHub Token
- [ ] 生成新Kimi API Key
- [ ] 生成新Jina API Key
- [ ] （可选）生成新Claude API Key
- [ ] 本地.env文件更新
- [ ] 测试所有API可用性

#### 阶段2：旧密钥撤销（10分钟）
- [ ] GitHub: 撤销旧Token
- [ ] Kimi: 删除旧Key
- [ ] Jina: 删除旧Key
- [ ] Claude: 删除旧Key（如有）

#### 阶段3：Git历史清理（20分钟）
- [ ] 备份.git目录
- [ ] 安装git-filter-repo
- [ ] 执行filter-repo清理
- [ ] 强制推送
- [ ] 验证清理结果

#### 阶段4：系统验证（15分钟）
- [ ] 测试GitHub推送
- [ ] 测试Kimi API调用
- [ ] 测试Jina API调用
- [ ] 测试GitHub Models
- [ ] 验证所有自动化任务正常

---

## 📞 紧急联系

如遇问题：
1. 立即停止操作
2. 从.git.backup恢复
3. 联系满意妞协助

---

*文档生成时间：2026-03-21 08:25*
*下次提醒：2026-03-27（下周四）08:13*
