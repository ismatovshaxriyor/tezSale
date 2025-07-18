from django.core.management.base import BaseCommand
from telegramBot.main import main  # bu yerda main() ichida bot polling bo'ladi

class Command(BaseCommand):
    help = 'Telegram botni ishga tushiradi'

    def handle(self, *args, **kwargs):
        main()
