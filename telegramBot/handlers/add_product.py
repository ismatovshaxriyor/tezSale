# telegram_bot/handlers/add_ad.py

from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from webhook.models import User, Product, Category, ProductImage
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async
from telegramBot.utils.decorators import require_register

# Conversation bosqichlari
TITLE, PRICE, CATEGORY, DESCRIPTION, CONDITION, WARRANTY, LOCATION, PHOTO = range(8)

# --- Helper funksiyalar ---
@sync_to_async
def get_or_create_user(telegram_id, full_name):
    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={'full_name': full_name}
    )
    return user, created

@sync_to_async
def create_product(user, title, price, category, description, condition, warranty, latitude, longitude):
    return Product.objects.create(
        owner=user,
        title=title,
        price=price,
        category=category,
        description=description,
        condition=condition,
        warranty=warranty,
        latitude=latitude,
        longitude=longitude
    )

@sync_to_async
def save_product_image(product, image_name, image_content):
    product_image = ProductImage.objects.create(
        product=product,
        image=ContentFile(image_content, name=image_name)
    )
    return product_image

@sync_to_async
def get_all_categories():
    categories = list(Category.objects.all())
    return categories

@require_register
async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data['photos'] = []
    await update.message.reply_text("E'lon sarlavhasini kiriting:")
    return TITLE

async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text
    await update.message.reply_text("Narxini kiriting (so'mda):")
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text)
        if price <= 0:
            await update.message.reply_text("Narx noldan katta bo'lishi kerak.")
            return PRICE
        context.user_data['price'] = price
    except ValueError:
        await update.message.reply_text("Iltimos, to'g'ri raqam kiriting.")
        return PRICE

    categories = await get_all_categories()
    if not categories:
        await update.message.reply_text("Kategoriyalar topilmadi. Administrator bilan bog'laning.")
        return ConversationHandler.END

    keyboard = [[c.name] for c in categories]
    context.user_data['categories'] = {c.name: c for c in categories}

    await update.message.reply_text(
        "Kategoriya tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CATEGORY

async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected = update.message.text
    categories = context.user_data.get('categories', {})

    if selected not in categories:
        await update.message.reply_text("Noto'g'ri kategoriya. Qaytadan tanlang.")
        return CATEGORY

    context.user_data['category'] = categories[selected]
    await update.message.reply_text("E'lon haqida ma'lumot bering:", reply_markup=ReplyKeyboardRemove())
    return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text
    keyboard = [["Yangi"], ["Ishlatilgan"]]
    await update.message.reply_text("Holatini tanlang:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CONDITION

async def get_condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text not in ["Yangi", "Ishlatilgan"]:
        await update.message.reply_text("Faqat 'Yangi' yoki 'Ishlatilgan' tanlang.")
        return CONDITION
    context.user_data['condition'] = 'new' if text == "Yangi" else 'used'
    await update.message.reply_text("Kafolat muddati (agar bo'lsa, aks holda '-' deb yozing):", reply_markup=ReplyKeyboardRemove())
    return WARRANTY

async def get_warranty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    warranty = update.message.text.strip()
    context.user_data['warranty'] = None if warranty == "-" else warranty
    await update.message.reply_text(
        "Iltimos, lokatsiyangizni yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Lokatsiyani yuborish", request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.location:
        await update.message.reply_text("Iltimos, lokatsiyani tugma orqali yuboring.")
        return LOCATION

    location = update.message.location
    context.user_data['latitude'] = location.latitude
    context.user_data['longitude'] = location.longitude

    await update.message.reply_text("Endi rasmlarni yuboring (bir nechta yuborishingiz mumkin):", reply_markup=ReplyKeyboardRemove())
    return PHOTO


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id

    # Ensure product is created only once
    if 'product' not in context.user_data:
        user, _ = await get_or_create_user(telegram_id, update.message.from_user.full_name)
        product = await create_product(
            user=user,
            title=context.user_data['title'],
            price=context.user_data['price'],
            category=context.user_data['category'],
            description=context.user_data['description'],
            condition=context.user_data['condition'],
            warranty=context.user_data['warranty'],
            latitude=context.user_data['latitude'],
            longitude=context.user_data['longitude']
        )
        context.user_data['product'] = product
    else:
        product = context.user_data['product']

    # Handle photos
    photos = update.message.photo
    if not photos:
        await update.message.reply_text("Iltimos, rasm yuboring.")
        return PHOTO

    # Process only the highest quality photo from the message
    photo = photos[-1]  # Get the highest resolution photo
    file = await photo.get_file()
    data = await file.download_as_bytearray()
    image_name = f"{product.id}_{photo.file_id}.jpg"

    # Check if photo was already saved
    if photo.file_id not in context.user_data['photos']:
        await save_product_image(product, image_name, data)
        context.user_data['photos'].append(photo.file_id)  # Track saved photo

    # Ask if user wants to add more photos
    keyboard = ReplyKeyboardMarkup([["✅ E'lonni yakunlash"]], resize_keyboard=True)
    await update.message.reply_text(
        "Rasm saqlandi. Yana rasm yuborasizmi yoki e'lonni yakunlaysizmi?",
        reply_markup=keyboard
    )
    return PHOTO

async def finish_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "✅ E'lonni yakunlash":
        await update.message.reply_text("✅ E'lon va rasmlar saqlandi!", reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text("Iltimos, quyidagi variantlardan birini tanlang.")
        return PHOTO

async def cancel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ E'lon berish bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END