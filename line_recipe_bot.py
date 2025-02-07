import os
import openai
import json
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

# 環境変数からAPIキーを取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/")
def home():
    return "RecipAI is running!", 200


# レシピを生成する関数
def generate_recipe(ingredients):
    prompt = f"""
    以下の食材を使ったレシピを作成してください。
    食材: {', '.join(ingredients)}
    出力フォーマット:
    1. レシピ名
    2. 材料リスト
    3. 作り方（ステップごとに）
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400
    
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    ingredients = user_text.split(',')  # カンマ区切りで食材をリスト化
    recipe = generate_recipe(ingredients)
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=recipe)
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("📩 メッセージを受信しました:", event.message.text)  # 受信したメッセージをログに出力
    user_text = event.message.text
    ingredients = user_text.split(',')  # カンマ区切りで食材をリスト化
    recipe = generate_recipe(ingredients)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=recipe)
    )
    print("✅ レシピを送信しました")  # レシピ送信が成功したかログに出力


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
