#-*- coding: utf-8 -*-

from flask import Flask, request, abort
import json
import base64
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ThingsEvent, ScenarioResult,
)

app = Flask(__name__)
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

@app.route("/")
def healthcheck():
    return 'OK'

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, request.headers['X-Line-Signature'])
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(ThingsEvent)
def handle_things_event(event):
    if event.things.type != "scenarioResult":
        return
    if event.things.result.result_code != "success":
        app.logger.warn("Error result: %s", event)
        return

#    button_state = int.from_bytes(base64.b64decode(event.things.result.ble_notification_payload), 'little')
#   if button_state > 0:
#        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Button is pressed! Sid test123"))

    payload_byte =base64.b64decode(event.things.result.ble_notification_payload);
    temperature_byte= payload_byte[0:2];
    humidity_byte= payload_byte[2];
    temperature = int.from_bytes(temperature_byte, 'little')/100.00;
#    humidity= int.from_bytes(humidity_byte, 'little');
#    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="T:"+str(temperature)+",H:"+str(humidity)));
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="溫度:"+str(temperature)+"℃,濕度:"+str(humidity_byte)+"%"));
#    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="T:"+str(temperature)));

if __name__ == "__main__":
    app.run(debug=True)
