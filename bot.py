
import re
import os
import yaml
import logging

from crisp_api import Crisp
from telegram import Update
from telegram.ext import Application, Defaults, MessageHandler, filters, ContextTypes

import handler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

# Load Config
try:
    f = open('config.yml', 'r')
    config = yaml.safe_load(f)
except FileNotFoundError as error:
    logging.warning('没有找到 config.yml，请复制 config.yml.example 并重命名为 config.yml')
    exit(1)

# Connect Crisp
try:
    crispCfg = config['crisp']
    client = Crisp()
    client.set_tier("plugin")
    client.authenticate(crispCfg['id'], crispCfg['key'])
    client.plugin.get_connect_account()
    client.website.get_website(crispCfg['website'])
except Exception as error:
    logging.warning('无法连接 Crisp 服务，请确认 Crisp 配置项是否正确')
    exit(1)

async def onReply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    website_id = config['crisp']['website']
    if msg.reply_to_message.text is not None:
        session_id = re.search(
            'session_\w{8}(-\w{4}){3}-\w{12}', msg.reply_to_message.text).group()
    elif msg.reply_to_message.caption is not None:
        session_id = re.search(
            'session_\w{8}(-\w{4}){3}-\w{12}', msg.reply_to_message.caption).group()
    query = {
        "type": "text",
        "content": msg.text,
        "from": "operator",
        "origin": "chat"
    }
    client.website.send_message_in_conversation(website_id, session_id, query)

def main():
    try:
        app = Application.builder().token(config['bot']['token']).defaults(Defaults(parse_mode='HTML')).build()
        # 启动 Bot
        if os.getenv('RUNNER_NAME') is not None:
            return
        app.add_handler(MessageHandler(filters.REPLY & filters.TEXT, onReply))
        app.job_queue.run_once(handler.exec,5,name='RTM')
        app.run_polling(drop_pending_updates=True)
    except Exception as error:
        logging.warning('无法启动 Telegram Bot，请确认 Bot Token 是否正确，或者是否能连接 Telegram 服务器')
        exit(1)


if __name__ == "__main__":
    main()