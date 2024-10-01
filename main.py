import logging
import os

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_usd_rate():
    try:
        logger.info("request USD through API")
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        response.raise_for_status()
        data = response.json()
        logger.info("success request USD")
        return data["rates"]["RUB"]
    except requests.RequestException as e:
        logger.error(f"Error while requesting USD through API: {e}")
        return None


async def start(update: Update, context):
    logger.info(f"User {update.effective_chat.id} start messaging")
    await update.message.reply_text("Добрый день. Как вас зовут?")


async def handle_name(update: Update, context):
    name = update.message.text
    logger.info(f"Get name: {name}")
    usd_rate = get_usd_rate()
    if usd_rate is not None:
        await update.message.reply_text(
            f"Рад знакомству, {name}! Курс доллара сегодня {usd_rate}р"
        )
        logger.info(f"Successfully send message to user {name}.")
    else:
        await update.message.reply_text(
            "К сожалению, не удалось получить курс доллара."
        )
        logger.warning(f"Error while sending message to user {name}.")


def app():

    load_dotenv()
    TOKEN = os.getenv("TOKEN")

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)
    )

    application.run_polling()


if __name__ == "__main__":
    app()
