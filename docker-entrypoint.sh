#!/bin/sh

# conver_to_array(){
#     local BOT_SEND_ID_env=$1
#     local IFS=","
#     str=""
#     for send_id in ${BOT_SEND_ID_env};do
#         str="$str    - ${send_id}\n"
#     done
#     result=`echo -e "${str}"`
# }
AUTOREPLY=`echo -e "${AUTOREPLY}"`
OPENAI_PAYLOAD=`echo -e "${OPENAI_PAYLOAD}"`

# if [ ! -e "/Crisp-Telegram-Bot/config.yml" ]; then
# conver_to_array ${BOT_SEND_ID}
cat > /Crisp-Telegram-Bot/config.yml << EOF
bot:
  token: ${BOT_TOKEN}
  groupId: ${BOT_GROUPID}
crisp:
  id: ${CRISP_ID}
  key: ${CRISP_KEY}
  website: ${CRISP_WEBSITE}
easyimages:
  apiUrl: ${EasyImages_apiUrl}
  apiToken: ${EasyImages_apiToken}
autoreply:
${AUTOREPLY}
openai:
  apiKey: ${OPENAI_APIKEY}
  payload: |
${OPENAI_PAYLOAD}
EOF
# fi
exec "$@"