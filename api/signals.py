# models.py yoki signals.py da
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User, created=True)
def activate_user(sender, instance, created, **kwargs):
    if created:
        instance.is_active = True
        instance.save()