
import os
import yaml
import logging
import requests

from openai import OpenAI
from crisp_api import Crisp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, Defaults, MessageHandler, filters, ContextTypes, CallbackQueryHandler

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

# Connect OpenAI
try:
    openai = OpenAI(api_key=config['openai']['apiKey'],base_url='https://api.openai.com/v1')
    openai.models.list()
except Exception as error:
    logging.warning('无法连接 OpenAI 服务，智能化回复将不会使用')
    openai = None

def changeButton(sessionId,boolean):
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                text='关闭 AI 回复' if boolean else '打开 AI 回复',
                callback_data=f'{sessionId},{boolean}'
                )
            ]
        ]
    )

async def onReply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message

    if msg.chat_id != config['bot']['groupId']:
        return
    for sessionId in context.bot_data:
        if context.bot_data[sessionId]['topicId'] == msg.message_thread_id:
            query = {
                "type": "text",
                "content": msg.text,
                "from": "operator",
                "origin": "chat",
                "user": {
                    "nickname": '人工客服',
                    "avatar": 'https://bpic.51yuansu.com/pic3/cover/03/47/92/65e3b3b1eb909_800.jpg'
                }
            }
            client.website.send_message_in_conversation(
                config['crisp']['website'],
                sessionId,
                query
            )
            return

# EasyImages Config
EASYIMAGES_API_URL = config.get('easyimages', {}).get('apiUrl', '')
EASYIMAGES_API_TOKEN = config.get('easyimages', {}).get('apiToken', '')

async def handleImage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    if msg.photo:
        file_id = msg.photo[-1].file_id
    elif msg.document and msg.document.mime_type.startswith('image/'):
        file_id = msg.document.file_id
    else:
        await msg.reply_text("请发送图片文件。")
        return

    try:
        # 获取文件下载 URL
        file = await context.bot.get_file(file_id)
        file_url = file.file_path

        # 上传图片到 EasyImages
        uploaded_url = upload_image_to_easyimages(file_url)

        # 生成 Markdown 格式的链接
        markdown_link = f"![Image]({uploaded_url})"

        # 查找对应的 Crisp 会话 ID
        session_id = get_target_session_id(context, msg.message_thread_id)
        if session_id:
            # 将 Markdown 链接推送给客户
            send_markdown_to_client(session_id, markdown_link)
            await msg.reply_text("图片已成功发送给客户！")
        else:
            await msg.reply_text("未找到对应的 Crisp 会话，无法发送给客户。")

    except Exception as e:
        await msg.reply_text("图片上传失败，请稍后重试。")
        logging.error(f"图片上传错误: {e}")

def upload_image_to_easyimages(file_url):
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        files = {
            'image': ('image.jpg', response.raw, 'image/jpeg'),
            'token': (None, EASYIMAGES_API_TOKEN)
        }
        res = requests.post(EASYIMAGES_API_URL, files=files)
        res_data = res.json()

        if res_data.get("result") == "success":
            return res_data["url"]
        else:
            raise Exception(f"Image upload failed: {res_data}")
    except Exception as e:
        logging.error(f"Error uploading image: {e}")
        raise

def get_target_session_id(context, thread_id):
    for session_id, session_data in context.bot_data.items():
        if session_data.get('topicId') == thread_id:
            return session_id
    return None

def send_markdown_to_client(session_id, markdown_link):
    try:
        # 将 Markdown 图片链接作为纯文本发送
        query = {
            "type": "text",
            "content": markdown_link,  # 将图片链接当做普通文本
            "from": "operator",
            "origin": "chat",
            "user": {
                "nickname": "人工客服",
                "avatar": "https://bpic.51yuansu.com/pic3/cover/03/47/92/65e3b3b1eb909_800.jpg"
            }
        }
        client.website.send_message_in_conversation(
            config['crisp']['website'],
            session_id,
            query
        )
        logging.info(f"图片链接已成功发送至 Crisp 会话 {session_id}")
    except Exception as e:
        logging.error(f"发送图片链接到 Crisp 失败: {e}")
        raise

async def onChange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    if openai is None:
        await query.answer('无法设置此功能')
    else:
        data = query.data.split(',')
        session = context.bot_data.get(data[0])
        session["enableAI"] = not eval(data[1])
        await query.answer()
        try:
             await query.edit_message_reply_markup(changeButton(data[0],session["enableAI"]))
        except Exception as error:
            print(error)

def main():
    try:
        app = Application.builder().token(config['bot']['token']).defaults(Defaults(parse_mode='HTML')).build()
        # 启动 Bot
        if os.getenv('RUNNER_NAME') is not None:
            return
        app.add_handler(MessageHandler(filters.TEXT, onReply))
        app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handleImage))
        app.add_handler(CallbackQueryHandler(onChange))
        app.job_queue.run_once(handler.exec,5,name='RTM')
        app.run_polling(drop_pending_updates=True)
    except Exception as error:
        logging.warning('无法启动 Telegram Bot，请确认 Bot Token 是否正确，或者是否能连接 Telegram 服务器')
        exit(1)


if __name__ == "__main__":
    main()
