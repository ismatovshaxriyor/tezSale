# telegram_bot/handlers/start.py

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Salom, {user.full_name}!\n\n"
        "📍 Bu bot orqali siz e'lon qo'shishingiz, ko'rishingiz yoki tahrirlashingiz mumkin.\n\n"
        "Quyidagi buyruqlardan foydalaning:\n"
        "🔹 /add - Yangi e'lon joylash\n"
        "🔹 /my_ads - Mening e'lonlarim\n"
        "🔹 /delete - E'lonni o'chirish\n"
        "🔹 /edit - E'lonni tahrirlash\n"
        "🔹 /cancel - Jarayonni bekor qilish\n\n"
        "Boshlash uchun /add buyrug-ini yuboring!"
    )
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("🌐 Web App Test", web_app=WebAppInfo(url="https://d877-95-214-211-249.ngrok-free.app/webhook/all/"))]
    ], resize_keyboard=True)

    await update.message.reply_text("Test Web App ochish uchun tugmani bosing:", reply_markup=keyboard)
