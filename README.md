# Crisp Telegram Bot via Python

一个简单的项目，让 Crisp 客服系统支持透过 Telegram Bot 来快速回复。
使用反馈、功能定制可加群：[https://t.me/dyPythonBot](https://t.me/dyPythonBot)

Python 版本需求 >= 3.9

## 现有功能
- 基于Crisp客服系统
- 自动推送文字、图片到指定聊天
- 基于Telegram话题群将消息分栏

## 计划功能
- 回复图片功能（需要Crisp订阅）
- 兼容GPT实现更智能的自动回复
- 基础回复语料库模型
- 客制化产品语料库模型

## 常规使用
```
# apt install git 如果你没有git的话
git clone https://github.com/DyAxy/Crisp-Telegram-Bot.git
# 进程常驻可参考 screen 或 nohup 或 systemctl
# 你需要安装好 pip3 的包管理
cd Crisp-Telegram-Bot
pip3 install -r requirements.txt
cp config.yml.example config.yml
nano config.yml
# 根据注释中的内容修改配置
python3 bot.py
```

## 申请 Telegram Bot Token

1. 私聊 [https://t.me/BotFather](https://https://t.me/BotFather)
2. 输入 `/newbot`，并为你的bot起一个**响亮**的名字
3. 接着为你的bot设置一个username，但是一定要以bot结尾，例如：`v2board_bot`
4. 最后你就能得到bot的token了，看起来应该像这样：`123456789:gaefadklwdqojdoiqwjdiwqdo`

## 创建 Telegram Topic 群

1. 创建一个群聊，并将申请的 Bot 拉进去
2. 在管理群中，打开话题 (Topic)，并将 Bot 设为管理员
3. 将 # 的话题设为置顶 (Pin)

## 申请 Crisp 以及 MarketPlace 插件

1. 注册 [https://app.crisp.chat/initiate/signup](https://app.crisp.chat/initiate/signup)
2. 完成注册后，网站ID在浏览器中即可找到，看起来应该像这样：`https://app.crisp.chat/settings/website/12345678-1234-1234-1234-1234567890ab/`
3. 其中 `12345678-1234-1234-1234-1234567890ab` 就是网站ID
4. 前往 MarketPlace， 需要重新注册账号 [https://marketplace.crisp.chat/](https://marketplace.crisp.chat/)
5. 点击 New Plugin，选择 Private，输入名字以及描述。会获得开发者ID和Key，可能会不够用。
6. 需要Production Key，点击 Ask a production token，再点击Add a Scope。
7. 需要 2 条read和write权限：`website:conversation:sessions` 和 `website:conversation:messages`
8. 保存后即可获得ID和Key，此时点击右上角 Install Plugin on Website 即可。