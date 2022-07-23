# VampireSurvivorsTrans
Vampire Survivors 机翻汉化工具

## 为什么会有这个工具？
- 最近在玩Vampire Survivors，但是翻译有些不全，并且后面貌似没啥人汉化了，于是想做个简单的工具一劳永逸的处理

## 思路：
1. 通过注册表找到Vampire Survivors的安装目录
2. 解析对应的翻译文件
3. 通过googletrans机翻一遍，然后写回

## 打包指令
`pyinstaller -F -i .\icon\tea.ico .\code\GameTrans.py`