# telegram_bot/handlers/register.py
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from webhook.models import User
from asgiref.sync import sync_to_async

FULL_NAME, PHONE = range(2)

async def start_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Iltimos, to'liq ismingizni yuboring:")
    return FULL_NAME

async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text

    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("📞 Raqamni yuborish", request_contact=True)]
    ], resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text("Iltimos, telefon raqamingizni yuboring:", reply_markup=keyboard)
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone_number = contact.phone_number
    full_name = context.user_data["full_name"]
    telegram_id = update.effective_user.id

    # Saqlash
    await sync_to_async(User.objects.update_or_create)(
        telegram_id=telegram_id,
        defaults={
            "full_name": full_name,
            "phone_number": phone_number
        }
    )

    await update.message.reply_text("✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!")
    return ConversationHandler.END

async def cancel_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Ro'yxatdan o'tish bekor qilindi.")
    return ConversationHandler.END
