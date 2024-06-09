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
    user_first_name = update.effective_user.first_name
    welcome_message = (
        f"👋 Hey there, {user_first_name}!\n\n"
        "Welcome!\n\n"
        "Ready for some fun? 🎉 Just upload a photo, and I'll tell you exactly how many pure black pixels (#000000) are hiding in it. It's that simple and cool!\n\n"
        "Go ahead, give it a try! 📸\n\n"
        "If you need any help, just type /help.\n\n"
        "Let's get started and uncover those hidden black pixels together! 🖤"
    )

    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context):
    help_message = (
        "👋 Need some help? No problem!\n\n"
        "Here’s how you can make the most of [Bot's Name]:\n\n"
        "📸 **Upload a Photo**: Simply upload any photo, and I'll count how many pure black pixels (#000000) are in it.\n\n"
        "🔍 **Main Commands**:\n"
        "- **/start**: Start the bot and get a welcome message.\n"
        "- **/help**: Show this help message.\n"
        # "- **/support**: Get in touch with our support team if you have any questions or need further assistance.\n\n"
        "Feel free to upload a photo anytime and let’s discover those black pixels together! 🖤\n\n"
        # "If you need more help, just type /support.\n\n"
        "Happy exploring!"
    )

    await update.message.reply_text(help_message)


async def photo_handler(update: Update, context):
    with tempfile.TemporaryDirectory() as temp_dir:
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_path = await photo_file.download_to_drive(
            os.path.join(temp_dir, photo_file.file_path.split("/")[-1])
        )
        filename = os.path.basename(file_path)

        true_black_percent = calculate_percent_black(os.path.join(temp_dir, filename))
        print(f"True Black: {true_black_percent:.2f}%")

    reply = await update.message.reply_text(
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


async def video_handler(update: Update, context):
    await update.message.reply_text(
        text="I know videos 🎥 are cool, but I can only handle images 🖼️. Share a photo with me instead!",
        reply_to_message_id=update.message.id,
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
application.add_handler(MessageHandler(filters.VIDEO, video_handler))


def main(request):
    return loop.run_until_complete(webhook(request))
