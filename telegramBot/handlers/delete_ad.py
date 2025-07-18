# telegram_bot/handlers/delete_ad.py

import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import ContextTypes
from webhook.models import User, Product, ProductImage
from telegramBot.utils.decorators import require_register
from django.conf import settings
from asgiref.sync import sync_to_async

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
def get_images_by_product_id(product_id):
    return list(ProductImage.objects.filter(product_id=product_id))

@sync_to_async
def get_product_by_id(product_id):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None

@sync_to_async
def delete_product(product):
    # Get all images related to the product
    images = ProductImage.objects.filter(product=product)
    for img in images:
        image_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print("err:", e)
    
    product.delete()

def get_absolute_image_url(image_path, request=None):
    """Generate a full absolute URL for the image."""
    base_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
    relative_url = image_path.lstrip('/')
    return f"{base_url}/{relative_url}"

@require_register
async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)

    if not user:
        await update.message.reply_text("Sizda hech qanday e'lon yo'q.")
        return

    products = await get_products_by_user(user)

    if not products:
        await update.message.reply_text("Sizda o'chirish uchun e'lon yo'q.")
        return

    for product in products:
        text = f"📌 <b>{product.title}</b>\n💰 {product.price} so'm"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑 O'chirish", callback_data=f"delete_{product.id}")]
        ])

        images = await get_images_by_product_id(product.id)
        if images:
            media_group = []
            for i, img in enumerate(images):
                image_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
                if os.path.exists(image_path):
                    try:
                        with open(image_path, 'rb') as image_file:
                            media = InputMediaPhoto(
                                media=image_file,
                                parse_mode="HTML",
                            )
                            media_group.append(media)
                    except Exception as e:
                        await update.message.reply_text(f"Rasm yuborishda xato: {img.image.name}", reply_markup=keyboard if i == 0 else None)
                else:
                    await update.message.reply_text(f"Rasm topilmadi: {img.image.name}", reply_markup=keyboard if i == 0 else None)
                
            if media_group:
                await context.bot.send_media_group(
                    chat_id=update.effective_chat.id,
                    media=media_group
                )
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")
        else:
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")

async def delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("delete_"):
        return 1

    product_id = query.data.split("_")[1]
    product = await get_product_by_id(product_id)

    if not product:
        await query.message.edit_text("❌ E'lon topilmadi yoki allaqachon o'chirilgan.")
        return 1

    await delete_product(product)
    try:
        await query.message.edit_caption(caption="✅ E'lon o'chirildi.", parse_mode="HTML")
    except:
        await query.message.edit_text("✅ E'lon o'chirildi.")