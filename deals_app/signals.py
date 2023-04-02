from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Deal


@receiver(post_delete, sender=Deal)
@receiver(post_save, sender=Deal)
def clear_cache(sender, **kwargs):
    """Очистка кэша в случае изменений в таблице сделок"""

    cache.clear()

