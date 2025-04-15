from flask import Flask, request, jsonify
import json
import hashlib
import hmac
import base64
import time
import urllib.parse
import os
import requests

app = Flask(__name__)

APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
TOKEN = os.getenv("TOKEN")
AES_KEY = os.getenv("AES_KEY")


@app.route("/")
def index():
    return "DingTalk Bot is running."


@app.route("/dingtalk/callback", methods=["POST"])
def callback():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "no data"}), 400

    # 验证 URL
    if "challenge" in data:
        return jsonify({
            "msg_signature": request.args.get("msg_signature"),
            "timestamp": request.args.get("timestamp"),
            "nonce": request.args.get("nonce"),
            "encrypt": data.get("encrypt"),
        })

    # 获取群ID和消息内容
    try:
        content = json.loads(data["encrypt"])
        event_type = content.get("EventType", "")
        if event_type == "chatbot_message":
            conversation_id = content["conversationId"]
            text = content["text"]["content"]
            sender_id = content["senderStaffId"]

            if "获取群ID" in text:
                reply_to_conversation(conversation_id, f"本群 OpenConversationId 是：{conversation_id}")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return "OK"


def get_access_token():
    url = "https://oapi.dingtalk.com/gettoken"
    params = {
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
    }
    resp = requests.get(url, params=params).json()
    return resp["access_token"]


def reply_to_conversation(conversation_id, content):
    access_token = get_access_token()
    url = f"https://oapi.dingtalk.com/v1.0/im/messages"
    headers = {
        "Content-Type": "application/json",
        "x-acs-dingtalk-access-token": access_token,
    }
    data = {
        "msgParam": json.dumps({"content": content}),
        "msgKey": "sampleText",
        "receiverOpenConversationId": conversation_id,
        "robotCode": APP_KEY
    }
    requests.post(url, headers=headers, data=json.dumps(data))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
