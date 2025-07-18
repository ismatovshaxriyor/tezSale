# telegram_bot/utils/decorators.py

from webhook.models import User
from asgiref.sync import sync_to_async
from functools import wraps

def require_register(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        telegram_id = update.effective_user.id

        user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()

        if not user or not user.full_name or not user.phone_number:
            await update.message.reply_text("❌ Siz ro'yxatdan o'tmagansiz. Iltimos, /register buyrug'idan foydalaning.")
            return

        return await func(update, context, *args, **kwargs)

    return wrapper
