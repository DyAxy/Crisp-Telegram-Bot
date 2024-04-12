import bot
import json
import base64
import socketio
import requests
from telegram.ext import ContextTypes

config = bot.config
client = bot.client
website_id = config["crisp"]["website"]

def getKey(content: str):
    if len(config["autoreply"]) > 0:
        for x in config["autoreply"]:
            keyword = x.split("|")
            for key in keyword:
                if key in content:
                    return True, config["autoreply"][x]
    return False, ""

async def sendTextMessage(message):
    session_id = message["session_id"]
    metas = client.website.get_conversation_metas(website_id, session_id)

    flow = ['📠<b>Crisp消息推送</b>','']
    if len(metas["email"]) > 0:
        email = metas["email"]
        flow.append(f'📧<b>电子邮箱</b>：{email}')
    if len(metas["data"]) > 0:
        if "Plan" in metas["data"]:
            Plan = metas["data"]["Plan"]
            flow.append(f"🪪<b>使用套餐</b>：{Plan}")
        if "UsedTraffic" in metas["data"] and "AllTraffic" in metas["data"]:
            UsedTraffic = metas["data"]["UsedTraffic"]
            AllTraffic = metas["data"]["AllTraffic"]
            flow.append(f"🗒<b>流量信息</b>：{UsedTraffic} / {AllTraffic}")

    flow.append(f"🧾<b>消息内容</b>：{message['content']}")
    result, autoreply = getKey(message["content"])
    if result is True:
        flow.append("")
        flow.append(f"💡<b>自动回复</b>：{autoreply}")
        query = {
            "type": "text",
            "content": autoreply,
            "from": "operator",
            "origin": "chat",
        }
        client.website.send_message_in_conversation(website_id, session_id, query)
    
    flow.append("")
    flow.append(f"🧷<b>Session</b>：<tg-spoiler>{session_id}</tg-spoiler>")
    
    text = '\n'.join(flow)
    for send_id in config["bot"]["send_id"]:
        await callbackContext.bot.send_message(
            chat_id=send_id, text=text)
    client.website.mark_messages_read_in_conversation(
        website_id,
        session_id,
        {"from": "user", "origin": "chat", "fingerprints": [message["fingerprint"]]},
    )

async def sendImageMessage(message):
    session_id = message["session_id"]

    flow = ['📠<b>Crisp消息推送</b>','']
    flow.append("")
    flow.append(f"🧷<b>Session</b>：<tg-spoiler>{session_id}</tg-spoiler>")
    text = '\n'.join(flow)

    for send_id in config["bot"]["send_id"]:
        await callbackContext.bot.send_photo(
            chat_id=send_id,
            photo=message["content"]["url"],
            caption=text
        )
    client.website.mark_messages_read_in_conversation(
        website_id,
        session_id,
        {"from": "user", "origin": "chat", "fingerprints": [message["fingerprint"]]},
    )

sio = socketio.AsyncClient(reconnection_attempts=5, logger=True)
# Def Event Handlers
@sio.on("connect")
async def connect():
    await sio.emit("authentication", {
        "tier": "plugin",
        "username": config["crisp"]["id"],
        "password": config["crisp"]["key"],
        "events": [
            "message:send",
            "session:set_data"
        ]})
@sio.on("unauthorized")
async def unauthorized(data):
    print('Unauthorized: ', data)
@sio.event
async def connect_error():
    print("The connection failed!")
@sio.event
async def disconnect():
    print("Disconnected from server.")
@sio.on("message:send")
async def messageForward(data):
    try:
        if data["type"] == "text":
            await sendTextMessage(data)
        elif data["type"] == "file" and str(data["content"]["type"]).count("image") > 0:
            await sendImageMessage(data)
        else:
            print("Unhandled Message Type : ", data["type"])
    except Exception as err:
        print(err)

# Meow!
def getCrispConnectEndpoints():
    url = "https://api.crisp.chat/v1/plugin/connect/endpoints"

    authtier = base64.b64encode(
        (config["crisp"]["id"] + ":" + config["crisp"]["key"]).encode("utf-8")
    ).decode("utf-8")
    payload = ""
    headers = {"X-Crisp-Tier": "plugin", "Authorization": "Basic " + authtier}
    response = requests.request("GET", url, headers=headers, data=payload)
    endPoint = json.loads(response.text).get("data").get("socket").get("app")
    return endPoint
# Connecting to Crisp RTM(WSS) Server
async def start_server():
    await sio.connect(
        getCrispConnectEndpoints(),
        transports="websocket",
        wait_timeout=10,
    )
    await sio.wait()
    
async def exec(context: ContextTypes.DEFAULT_TYPE):
    global callbackContext
    callbackContext = context
    # await sendAllUnread()
    await start_server()