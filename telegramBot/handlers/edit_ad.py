# telegram_bot/handlers/edit_ad.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from webhook.models import User, Product
from telegramBot.utils.decorators import require_register
from django.conf import settings
from asgiref.sync import sync_to_async
import os

# Constants
SELECT_PRODUCT, EDIT_FIELD, EDIT_INPUT = range(3)  # Added SELECT_PRODUCT state
FIELD_NAMES = {
    "title": "yangi sarlavhani",
    "price": "yangi narxni",
    "description": "yangi tavsifni"
}
VALID_FIELDS = ["title", "price", "description"]

@sync_to_async
def get_user_by_telegram_id(telegram_id):
    try:
        return User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return None

@sync_to_async
def get_products_by_user(user):
    return list(Product.objects.filter(owner=user))

@sync_to_async
def get_product_by_id(product_id):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None

@sync_to_async
def update_product_field(product, field, value):
    setattr(product, field, value)
    product.save()

@require_register
async def edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear previous user_data to avoid conflicts
    context.user_data.clear()
    
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)

    if not user:
        await update.message.reply_text("Siz ro'yxatdan o'tmagansiz. Iltimos, avval ro'yxatdan o'ting.")
        return ConversationHandler.END

    products = await get_products_by_user(user)

    if not products:
        await update.message.reply_text("Tahrirlash uchun hech qanday e'lon topilmadi.")
        return ConversationHandler.END

    # Send product list with edit buttons
    for product in products:
        text = f"📌 <b>{product.title}</b>\n💰 {product.price} so'm"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✏ Tahrirlash", callback_data=f"edit_{product.id}")]
        ])

        if product.image:
            image_path = os.path.join(settings.MEDIA_ROOT, product.image.name)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as image_file:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=image_file,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
            else:
                await update.message.reply_text(
                    f"Rasm topilmadi: {text}",
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
        else:
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")

    return SELECT_PRODUCT  

async def edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("edit_"):
        await query.message.reply_text("Noto'g'ri buyruq.")
        return ConversationHandler.END

    product_id = query.data.split("_")[1]
    context.user_data['edit_product_id'] = product_id

    # Create field selection buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Sarlavha", callback_data="edit_field_title")],
        [InlineKeyboardButton("💰 Narx", callback_data="edit_field_price")],
        [InlineKeyboardButton("🧾 Tavsif", callback_data="edit_field_description")],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_edit")]
    ])

    try:
        await query.message.edit_text(
            text="Qaysi ma'lumotni tahrirlaysiz?",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        await query.message.reply_text(
            "Qaysi ma'lumotni tahrirlaysiz?",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    return EDIT_FIELD  # Transition to EDIT_FIELD state

async def edit_field_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("edit_field_"):
        await query.message.reply_text("Noto'g'ri maydon tanlandi.")
        return ConversationHandler.END

    field = query.data.replace("edit_field_", "")
    if field not in VALID_FIELDS:
        await query.message.reply_text("Noto'g'ri maydon tanlandi.")
        return ConversationHandler.END

    context.user_data['edit_field'] = field

    await query.message.edit_text(f"Iltimos, {FIELD_NAMES[field]} yuboring:")
    return EDIT_INPUT

async def edit_update_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_id = context.user_data.get('edit_product_id')
    field = context.user_data.get('edit_field')

    if not product_id or not field:
        await update.message.reply_text("Tahrirlash jarayonida xato yuz berdi.")
        return ConversationHandler.END

    if field not in VALID_FIELDS:
        await update.message.reply_text("Noto'g'ri maydon tanlandi.")
        return ConversationHandler.END

    value = update.message.text
    product = await get_product_by_id(product_id)

    if not product:
        await update.message.reply_text("E'lon topilmadi.")
        return ConversationHandler.END

    if field == "price":
        try:
            value = float(value)
            if value <= 0:
                await update.message.reply_text("Narx noldan katta bo'lishi kerak.")
                return EDIT_INPUT
        except ValueError:
            await update.message.reply_text("Narx noto'g'ri formatda. Iltimos, raqam kiriting.")
            return EDIT_INPUT

    await update_product_field(product, field, value)
    await update.message.reply_text(f"✅ {FIELD_NAMES[field]} yangilandi: {value}")
    context.user_data.clear()  
    return ConversationHandler.END

async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Tahrirlash bekor qilindi.")
    context.user_data.clear()  
    return ConversationHandler.END