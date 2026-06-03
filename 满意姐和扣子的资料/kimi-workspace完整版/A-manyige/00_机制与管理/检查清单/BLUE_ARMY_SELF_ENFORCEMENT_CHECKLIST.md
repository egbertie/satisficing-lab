# 蓝军自我审计强制检查清单

**创建时间**: 2026-03-30 07:59  
**创建原因**: 用户质问蓝军为什么还在MD阶段，要求学习满意妞升级  
**执行方式**: 每次审计后必须运行 `scripts/blue_army_self_enforcement_check.sh`

---

## 一、蓝军强制执行检查（10项）

每次审计后，必须逐项检查：

### 语言检查
- [ ] **说"必须"，不说"建议"**
  - 检查：本次审计报告中是否有"建议"、"可以考虑"、"建议优先"
  - 标准：0次出现
  - 违规：每出现1次，自扣5分

- [ ] **说"FAIL"，不说"基本合格"**
  - 检查：审计结论是否只有PASS/FAIL两种
  - 标准：无二义性结论
  - 违规：出现"基本"、"差不多"、"有进步"等模糊词，FAIL

### 思维方式应用检查
- [ ] **应用至少3项思维方式**
  - 检查：审计报告中是否明确展示思维方式应用
  - 标准：至少3项，有具体应用展示
  - 违规：少于3项，FAIL

- [ ] **五层深挖完整**
  - 检查：发现问题后是否追问5 Why
  - 标准：表象→原因→根因→预防→能力
  - 违规：少于5层，FAIL

### 抽查范围检查
- [ ] **抽查比例达标**
  - 标准：第一阶段至少10%（94个Skill至少抽查10个）
  - 违规：少于10%，FAIL

- [ ] **发现问题后扩大抽查**
  - 检查：发现问题后是否扩大到50%或全量
  - 标准：问题率>20%必须全量
  - 违规：未扩大，FAIL

### FAIL完整性检查
- [ ] **问题描述具体**
  - 检查：FAIL的问题描述是否可验证
  - 标准：有具体数据、文件路径、现象
  - 违规：模糊描述，FAIL

- [ ] **要求明确可执行**
  - 检查：要求是否具体到动作
  - 标准：动词+对象+标准
  - 违规：抽象要求，FAIL

- [ ] **时限明确**
  - 检查：每个要求是否有明确截止时间
  - 标准：具体日期时间
  - 违规："尽快"、"尽快完成"，FAIL

- [ ] **后果明确**
  - 检查：未完成有什么后果
  - 标准：扣分/重做/阻断/用户介入
  - 违规：无后果或"下次注意"，FAIL

---

## 二、执行机制

### 执行脚本
```bash
./scripts/blue_army_self_enforcement_check.sh
```

### 升级脚本
```bash
./scripts/blue_army_audit_upgrade.sh 94 10 3
# 参数: 总数 已抽查 发现问题
```

### 监督脚本
```bash
./scripts/satisfying_girl_supervision.sh
```

---

## 三、违规自罚

| 违规项 | 自罚 | 记录位置 |
|--------|------|----------|
| 说"建议" | -5分 | diary/blue-army-punishment.log |
| 未应用思维方式 | -10分 | diary/blue-army-punishment.log |
| 抽查不足10% | -10分 | diary/blue-army-punishment.log |
| 发现问题未扩大 | -15分 | diary/blue-army-punishment.log |
| FAIL不完整 | -5分/项 | diary/blue-army-punishment.log |

---

## 四、满意妞执行监督

每日运行监督脚本，检查满意妞是否执行蓝军要求：

```bash
./scripts/satisfying_girl_supervision.sh
```

**超期处理**:
- 发现超期 → 立即向用户申请介入
- 临近截止（剩余<20%时间）→ 提醒满意妞

---

## 五、物理证据验证

用户可随时验证：

```bash
# 检查脚本是否存在
ls -la scripts/blue_army_self_enforcement_check.sh
ls -la scripts/blue_army_audit_upgrade.sh
ls -la scripts/satisfying_girl_supervision.sh

# 检查是否可执行
./scripts/blue_army_self_enforcement_check.sh
./scripts/satisfying_girl_supervision.sh
```

---

*可执行机制已建立，不再只是MD文件*
