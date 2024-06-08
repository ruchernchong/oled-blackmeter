import asyncio
import html
import json
import logging
import os
import tempfile
import traceback

from dotenv import load_dotenv
from telegram import Update, Bot, constants
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from calculator import calculate_percent_black

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def start(update: Update, context):
    print("START COMMAND")
    await update.message.reply_text("Hello! Welcome to the bot.")


async def help_command(update: Update, context):
    print("HELP COMMAND")
    await update.message.reply_text("This is a help message.")


async def photo_handler(update: Update, context):
    print("PHOTO HANDLER")
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


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id="61755098", text=message, parse_mode=ParseMode.HTML
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
application.add_error_handler(error_handler)


def main(request):
    return loop.run_until_complete(webhook(request))
