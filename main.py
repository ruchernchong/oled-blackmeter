import asyncio
import os
import tempfile

from dotenv import load_dotenv
from telegram import Update, Bot, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from calculator import calculate_percent_black

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def start(update: Update, context):
    await update.message.reply_text("Hello! Welcome to the bot.")


async def help_command(update: Update, context):
    await update.message.reply_text("This is a help message.")


async def photo_handler(update: Update, context):
    with tempfile.TemporaryDirectory() as temp_dir:
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_path = await photo_file.download_to_drive(
            os.path.join(temp_dir, photo_file.file_path.split("/")[-1])
        )
        filename = os.path.basename(file_path)

        true_black_percent = calculate_percent_black(os.path.join(temp_dir, filename))
        print(f"True Black: {true_black_percent}")

    reply = await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"True Black: {true_black_percent:.2f}%",
        reply_to_message_id=update.message.message_id,
    )

    if true_black_percent == 100.0:
        await context.bot.set_message_reaction(
            chat_id=update.message.chat_id,
            message_id=reply.message_id,
            reaction=constants.ReactionEmoji.HUNDRED_POINTS_SYMBOL,
        )

    await context.bot.set_message_reaction(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        reaction=constants.ReactionEmoji.THUMBS_UP,
    )


async def webhook(request):
    if request.method == "POST":
        update = Update.de_json(request.get_json(), bot)
        await application.initialize()
        await bot.initialize()
        await application.process_update(update)
        await application.shutdown()
        return "OK", 200


application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.PHOTO, photo_handler))


def main(request):
    return loop.run_until_complete(webhook(request))
