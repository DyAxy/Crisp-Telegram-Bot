FROM python:3.11-alpine AS build
ADD requirements.txt /build/requirements.txt
WORKDIR /build
RUN apk update
RUN apk add --no-cache --virtual .build-deps git build-base libffi-dev libstdc++
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt
RUN apk del .build-deps

FROM python:3.11-alpine
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
ADD / /Crisp_Telegram_Bot
WORKDIR /Crisp_Telegram_Bot
ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD ["python3","bot.py"]