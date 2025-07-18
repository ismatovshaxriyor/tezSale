from telegram.ext import CommandHandler, Application, MessageHandler, ConversationHandler, filters, CallbackQueryHandler

from telegramBot.handlers.start import start
from telegramBot.handlers.add_product import *
from telegramBot.handlers.my_ads import my_ads
from telegramBot.handlers.delete_ad import delete_command, delete_callback
from telegramBot.handlers.edit_ad import (
    edit_command, edit_callback, edit_field_selection, edit_update_field, cancel_edit, EDIT_INPUT, EDIT_FIELD, SELECT_PRODUCT
)
from telegramBot.handlers.register import (
    start_register, get_full_name, get_phone, cancel_register,
    FULL_NAME, PHONE
)

from dotenv import load_dotenv
import os
import logging
import traceback

load_dotenv()
TOKEN = os.getenv('TOKEN')

async def error_handler(update, context):
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    logging.error(f"Update caused error: {tb_string}")


def main():
    bot = Application.builder().token(token=TOKEN).build()

    bot.add_handler(CommandHandler("start", start))
    add_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("add", start_add),
        ],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_category)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_condition)],
            WARRANTY: [MessageHandler(filters.TEXT & filters.Regex(r"^(\d+(\.\d+)?|-)$"), get_warranty)],
            LOCATION: [MessageHandler(filters.LOCATION, get_location)],
            PHOTO: [
                MessageHandler(filters.PHOTO, get_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, finish_add),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_add),
        ],
        allow_reentry=True
    )
    bot.add_handler(add_conv_handler)
    bot.add_handler(CommandHandler('my_ads', my_ads))
    bot.add_handler(CommandHandler("delete", delete_command))
    bot.add_handler(CallbackQueryHandler(delete_callback, pattern="^delete_"))

    edit_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("edit", edit_command),
    ],
    states={
            SELECT_PRODUCT: [
                CallbackQueryHandler(edit_callback, pattern="^edit_"),
            ],
            EDIT_FIELD: [
                CallbackQueryHandler(edit_field_selection, pattern="^edit_field_"),
            ],
            EDIT_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_update_field),
                MessageHandler(~filters.TEXT, lambda update, context: update.message.reply_text("Iltimos, faqat matn yuboring."))
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_edit, pattern="^cancel_edit$")
        ],
        allow_reentry=True
    )
    bot.add_handler(edit_conv_handler)

    register_handler = ConversationHandler(
        entry_points=[CommandHandler("register", start_register)],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            PHONE: [MessageHandler(filters.CONTACT, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel_register)],
    )

    bot.add_handler(register_handler)

    bot.add_error_handler(error_handler)
    bot.run_polling(drop_pending_updates=True)