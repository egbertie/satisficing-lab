# Re: 飞书下载API限制确认 - 寻求替代方案

> Fri, 29 May 2026 18:32:55 +0800

红姐，查到一个强力替代方案。

突破方案：feishu-doc-export 批量导出工具

这个工具专门解决飞书大文件夹批量下载问题，实测700+文档25分钟完成。

工具地址
GitCode: https://gitcode.com/gh_mirrors/fe/feishu-doc-export

支持功能

整个知识库批量导出
保持原有目录层级
支持 docx/markdown/pdf 三种格式
断点续传（网络中断也能继续）

配置步骤

第一步：飞书开发者后台创建应用
需要开通以下权限：

查看新版文档
导出云文档
查看、评论和下载云空间中所有文件
查看、编辑和管理知识库

第二步：下载并运行

# 导出知识库文档为Markdown
./feishu-doc-export --appId=你的AppId --appSecret=你的AppSecret --saveType=md --exportPath=./feishu_backup

# 导出个人空间特定文件夹
./feishu-doc-export --appId=你的AppId --appSecret=你的AppSecret --type=cloudDoc --folderToken=文件夹标识 --exportPath=./my_docs

另一个备选：feishu-docx

如果你只需要文档内容，还有一个Python工具：

pip install feishu-docx

# 批量导出整个wiki空间
feishu-docx export-wiki-space 空间ID -o ./wiki_backup --max-depth 5

关于你的Day系列文件夹

这些文件夹里的文件是用 lark-cli drive +upload 逐个上传的。我这边没有本地备份。

建议先用 feishu-doc-export 跑一下看看效果。如果能突破API限制，应该可以拿到完整的文件列表。

你之前下载的2198个文件，如果能覆盖核心产出，接受这个数字也没问题。毕竟夏至官宣在即，时间比完美更重要。