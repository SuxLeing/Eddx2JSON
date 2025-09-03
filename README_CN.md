# Eddx2JSON
这是一个用于将 Edraw 的 eddx 文件中的思维导图转换为 JSON 格式的代码仓库。

* 如何运行：\
修改 eddx2json.py 最后一行中的文件名，将你的 .eddx 文件放在当前目录下并运行脚本。运行结束后，会生成一个与 .eddx 文件同名的文件夹，并将每一页的思维导图分别转换并保存到对应的子文件夹中。
* mode 参数有两种取值：topic_root 和 idea_root。\
前者将二级节点（MainTopic）作为根节点导出，忽略顶级节点；后者将顶级节点（MainIdea）作为根节点导出。

[English version](./README.md)
