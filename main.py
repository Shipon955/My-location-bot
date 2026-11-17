import logging
import requests
import phonenumbers

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

TOKEN = "YOUR_BOT_TOKEN"

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Location Info Bot!\n\n"
        "/ip IP_ADDRESS\n"
        "/phone PHONE_NUMBER\n"
        "/help"
    )


async def ip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ip 8.8.8.8")
        return

    ip = context.args[0]

    try:
        response = requests.get(
            f"https://ipwho.is/{ip}",
            timeout=10
        )
        data = response.json()

        if not data.get("success"):
            await update.message.reply_text("Invalid IP address.")
            return

        result = (
            f"Country: {data.get('country')}\n"
            f"City: {data.get('city')}\n"
            f"Region: {data.get('region')}\n"
            f"ISP: {data.get('connection', {}).get('isp')}\n"
            f"Timezone: {data.get('timezone', {}).get('id')}\n\n"
            "Location is approximate."
        )

        await update.message.reply_text(result)

    except Exception:
        await update.message.reply_text("Could not retrieve IP information.")


async def phone_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /phone +8801XXXXXXXXX")
        return

    number = " ".join(context.args)

    try:
        parsed = phonenumbers.parse(number, None)

        if not phonenumbers.is_possible_number(parsed):
            await update.message.reply_text("Invalid phone number.")
            return

        from phonenumbers import geocoder

        country = geocoder.description_for_number(parsed, "en")

        await update.message.reply_text(
            f"Country/Region: {country}\n"
            f"Country Code: +{parsed.country_code}\n"
            f"Valid: {phonenumbers.is_valid_number(parsed)}\n\n"
            "This does not reveal live location."
        )

    except Exception:
        await update.message.reply_text("Use international format, e.g. +8801XXXXXXXXX")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/start - Start bot\n"
        "/ip - IP information\n"
        "/phone - Phone country information"
    )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ip", ip_info))
app.add_handler(CommandHandler("phone", phone_info))
app.add_handler(CommandHandler("help", help_command))

app.run_polling()
