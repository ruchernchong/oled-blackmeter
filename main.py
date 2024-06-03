import os
import tempfile

import telegram.constants
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from calculator import calculate_percent_black

load_dotenv()


# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! Welcome to the bot.")


# Function to handle the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("This is a help message.")


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            reaction=telegram.constants.ReactionEmoji.HUNDRED_POINTS_SYMBOL,
        )

    await context.bot.set_message_reaction(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        reaction=telegram.constants.ReactionEmoji.THUMBS_UP,
    )


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
