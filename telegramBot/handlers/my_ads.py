# telegram_bot/handlers/my_ads.py

import logging
import os
from telegram import Update, InputMediaPhoto
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
def get_user_products(user):
    return list(Product.objects.filter(owner=user).select_related('category').order_by('-created_at'))

@sync_to_async
def get_images_by_product_id(product_id):
    return list(ProductImage.objects.filter(product_id=product_id))

@require_register
async def my_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)

    if not user:
        await update.message.reply_text("Siz hali birorta e'lon joylamagansiz.")
        return

    products = await get_user_products(user)

    if not products:
        await update.message.reply_text("Sizda hozircha hech qanday e'lon yo'q.")
        return

    for product in products:
        category_name = product.category.name if product.category else 'Yoq'
        created_at = product.created_at.strftime('%Y-%m-%d %H:%M')

        caption = (
            f"📌 <b>{product.title}</b>\n"
            f"💰 Narxi: {product.price} so'm\n"
            f"🏷️ Kategoriya: {category_name}\n"
            f"🕒 Sana: {created_at}"
        )

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
                                caption=caption if i == 0 else None,
                                parse_mode="HTML"
                            )
                            media_group.append(media)
                    except Exception as e:
                        await update.message.reply_text(f"Rasm yuborishda xato: {img.image.name}")
                else:
                    await update.message.reply_text(f"Rasm topilmadi: {img.image.name}")

            if media_group:
                await context.bot.send_media_group(
                    chat_id=update.effective_chat.id,
                    media=media_group
                )
        else:
            await update.message.reply_text(caption, parse_mode="HTML")