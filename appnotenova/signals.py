from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
import json
from .models import NewsEntry


from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NewsEntry

@receiver(post_save, sender=NewsEntry)
def handle_post_save(sender, instance, created, **kwargs):
    # Only send to Chime if explicitly requested
    if hasattr(instance, '_send_to_chime') and instance._send_to_chime:
        # Don't do anything here as it's handled in admin
        pass
