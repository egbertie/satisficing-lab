# 满意解研究所 · 微信小程序

## 小程序结构

```
miniapp/
├── app.json               # 全局配置
├── app.js                 # 入口
├── app.wxss               # 全局样式
├── project.config.json    # 项目配置
└── pages/index/
    ├── index.json         # 页面配置
    ├── index.wxml         # web-view 嵌入H5测评页
    ├── index.js           # 页面逻辑
    └── index.wxss         # 页面样式
```

## 原理

使用微信小程序 `<web-view>` 组件，将 GitHub Pages 上的 H5 测评页面嵌入。

## 使用步骤

1. 下载微信开发者工具: https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
2. 打开「满意解研究所」小程序项目，导入 `miniapp/` 目录
3. 在小程序管理后台 → 开发 → 开发管理 → 开发设置 → 服务器域名 → 添加 `https://egbertie.github.io` 到 request合法域名
4. 上传代码 → 提交审核 → 发布
