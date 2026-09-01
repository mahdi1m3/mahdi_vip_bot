"""
ربات تلگرام کلاب VIP مهدی ایرانی
------------------------------------------
این فایل یک ربات ساده تلگرام است که:
  1) با دستور /start پیام خوش‌آمدگویی + دکمه‌های شیشه‌ای پایین صفحه (Reply Keyboard) را نشان می‌دهد.
  2) با کلیک روی هر دکمه، پاسخ مناسب را ارسال می‌کند.

این کد برای هاست شدن روی Render (به‌صورت Web Service رایگان) آماده شده است.
چون سرویس‌های رایگان Render نیاز به یک پورت باز دارند، یک وب‌سرور کوچک Flask
در کنار ربات اجرا می‌شود که فقط برای «زنده نگه داشتن» سرویس است و کار خاصی انجام نمی‌دهد.

نحوه اجرا در Render در فایل README.md توضیح داده شده است.
"""

import os
import logging
import threading

from flask import Flask
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ----------------------------------------------------------------------------
# تنظیمات پایه
# ----------------------------------------------------------------------------

# توکن ربات را از متغیر محیطی (Environment Variable) می‌خوانیم.
# هرگز توکن را مستقیم داخل کد ننویسید (به‌خصوص اگر کد را جایی عمومی قرار می‌دهید).
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# متن دکمه‌ها — اگر بخواهید متن دکمه‌ها را عوض کنید، فقط همین‌جا تغییرشان دهید
BTN_SUPPORT = "🎧 پشتیبانی"
BTN_FREE_VIP = "💎 VIP رایگان"

# آیدی پشتیبان — این را با آیدی تلگرام واقعی خودتان جایگزین کنید
SUPPORT_USERNAME = "@YourSupportUsername"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# هندلرها (پاسخ‌دهنده‌ها)
# ----------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /start"""

    welcome_text = (
        "سلام! به کلاب VIP مهدی ایرانی خوش آمدید 👑\n"
        "از دکمه‌های زیر برای دسترسی به بخش‌های مختلف استفاده کنید:"
    )

    # ساخت کیبورد متنی (Reply Keyboard) — دو دکمه در یک سطر
    keyboard = [[BTN_SUPPORT, BTN_FREE_VIP]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,   # اندازه دکمه‌ها را کوچک و مرتب می‌کند
        one_time_keyboard=False # کیبورد بعد از هر کلیک بسته نمی‌شود
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دکمه پشتیبانی"""
    text = (
        "🎧 پشتیبانی\n\n"
        f"برای ارتباط با پشتیبانی می‌توانید به آیدی زیر پیام دهید:\n"
        f"{SUPPORT_USERNAME}\n\n"
        "تیم پشتیبانی در سریع‌ترین زمان ممکن پاسخگوی شما خواهد بود."
    )
    await update.message.reply_text(text)


async def handle_free_vip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دکمه VIP رایگان"""
    text = (
        "💎 عضویت VIP رایگان\n\n"
        "برای دریافت دسترسی رایگان به کانال VIP، شرایط زیر را رعایت کنید:\n"
        "۱. ثبت‌نام از طریق لینک رفرال ما\n"
        "۲. ارسال اسکرین‌شات یا آیدی حساب برای تأیید\n"
        "۳. تأیید نهایی توسط ادمین\n\n"
        "پس از تأیید، لینک عضویت در کانال VIP برای شما ارسال می‌شود."
    )
    await update.message.reply_text(text)


async def handle_unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """اگر کاربر متنی غیر از دکمه‌ها بفرستد"""
    await update.message.reply_text(
        "لطفاً از دکمه‌های پایین صفحه استفاده کنید، یا دستور /start را بفرستید."
    )


# ----------------------------------------------------------------------------
# راه‌اندازی ربات (Polling)
# ----------------------------------------------------------------------------

def run_bot() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "متغیر محیطی BOT_TOKEN تنظیم نشده است. "
            "توکن ربات را در تنظیمات Environment Variables سرویس Render وارد کنید."
        )

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_SUPPORT}$"), handle_support))
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_FREE_VIP}$"), handle_free_vip))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown_text))

    logger.info("ربات در حال اجرا (polling)...")
    application.run_polling(drop_pending_updates=True)


# ----------------------------------------------------------------------------
# وب‌سرور کوچک برای زنده نگه داشتن سرویس روی Render (Web Service رایگان)
# ----------------------------------------------------------------------------

flask_app = Flask(__name__)


@flask_app.route("/")
def health_check():
    return "Bot is running.", 200


def run_flask() -> None:
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    # ربات را در یک ترد جدا اجرا می‌کنیم تا وب‌سرور Flask بتواند هم‌زمان پورت را باز نگه دارد
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    run_flask()
