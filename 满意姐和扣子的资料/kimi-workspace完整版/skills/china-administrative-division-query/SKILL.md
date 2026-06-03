---
name: "get-xzqh"
description: "用于获取各级行政区划（省、市、区县、乡镇）数据。当用户要求实现省市区联动、获取下属行政区或查询相关区划代码时调用此技能。"
---

# 获取行政区划 (Get Administrative Divisions)

本技能用于通过民政部地名服务接口获取全国各级行政区划数据。

## 接口说明

- **接口地址**: `https://dmfw.mca.gov.cn/9095/xzqh/getList`
- **请求方式**: GET

## 参数规范 (GET Parameters)

直接拼接在 URL 后进行请求：

- `code`: 父级区划代码（为空则代表全国）
- `maxLevel`: 获取的区划层级
  - `1` = 省 (Province)
  - `2` = 市 (City)
  - `3` = 区县 (District/County)
  - `4` = 乡镇 (Township)

## 典型示例 (Examples)

1. **全国省级**: 
   `https://dmfw.mca.gov.cn/9095/xzqh/getList?maxLevel=1`

2. **山东（37）下所有市**: 
   `https://dmfw.mca.gov.cn/9095/xzqh/getList?code=37&maxLevel=2`

3. **青岛（3702）下所有区县**: 
   `https://dmfw.mca.gov.cn/9095/xzqh/getList?code=3702&maxLevel=3`

4. **黄岛区（370211）下所有乡镇**: 
   `https://dmfw.mca.gov.cn/9095/xzqh/getList?code=370211&maxLevel=4`

## 触发场景 (When to invoke)

当用户提出与“行政区划”、“省市区联动”、“获取下级区划”等相关的需求时，可参考本接口的传参规则进行代码编写或数据请求。
