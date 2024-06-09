import asyncio
import os
import subprocess
import time

from dotenv import load_dotenv
from flask import Flask, request
from telegram import Bot

from main import webhook

load_dotenv()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

NGROK_STATIC_DOMAIN = os.getenv("NGROK_STATIC_DOMAIN")

app = Flask(__name__)


def start_ngrok():
    try:
        subprocess.run(["ngrok", "start", "flask"])
        time.sleep(3)
        print("ngrok URL", f"https://{NGROK_STATIC_DOMAIN}")
    except Exception as e:
        print("Error starting ngrok", e)


async def set_webhook():
    bot = Bot(token=os.environ.get("TELEGRAM_BOT_TOKEN"))
    webhook_url = f"https://{NGROK_STATIC_DOMAIN}/webhook"

    try:
        await bot.setWebhook(url=webhook_url)
        print(f"Webhook set to {webhook_url}")
    except Exception as e:
        print("Error setting webhook", e)


@app.post("/webhook")
def main():
    return loop.run_until_complete(webhook(request))


if __name__ == "__main__":
    asyncio.run(set_webhook())
    # start_ngrok()
    app.run()
