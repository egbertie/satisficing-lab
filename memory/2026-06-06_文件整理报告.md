# 2026-06-06 workspace 文件整理报告

> 23:53 CST · 根目录从 347 项 → 50 项

## 整理前
- 267 个 HTML 文件散落根目录
- 6 个 JSON 数据文件裸放
- 3 个 Logo/图片散落
- Python/Shell/JS/CSS 共 10+ 个文件散落
- site symlink (broken)

## 整理后
所有历史文件归入 `_site-archive/`:

```
_site-archive/
├── html/      267个HTML (已存在于 satisficing-lab/ 中)
├── frontend/  JS/CSS 文件
├── json-data/ entities_index/file_index/import_data/product_catalog/open_tasks_audit
├── scripts/   portal-server.py · start-fb.sh · start-portal.sh · devserver.py · feishu-notify.js · vi_audit.sh
├── logos/     sri_compass_logo.png · sri_dingyu_logo.png · sri_main_logo.jpg
└── other/     dashboard.html.bak2 · linkedin-bio.txt · robots.txt · sitemap.xml · vi_quick_ref.css · .portal-* · .trigger-pages · .nojekyll
```

## 保留在根目录的 (50项)
只保留:
- `*.md` 配置文件 (MEMORY/SOUL/AGENTS/IDENTITY/USER/HEARTBEAT/READ/SITE_HANDBOOK/DEPLOY/CHANGELOG)
- 活跃目录: satisficing-lab/ memory/ Projects/ scripts/ server/ assets/ skills/ deep/ light/ rem/ miniapp/
- `dev.sh` (活跃开发工具)
- 私有: .git/ .clawhub/ .openclaw/ .bak/

## 空间释放
- 散落文件: 20MB → 归入 _site-archive/
- satisficing-lab/ 保持唯一主项目目录
