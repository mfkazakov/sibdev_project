from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Deal, DealV2, Customer, Gem


@receiver(post_delete, sender=Deal)
@receiver(post_save, sender=Deal)
def clear_cache(sender, **kwargs):
    """Очистка кэша в случае изменений в таблице сделок"""
    cache.delete('response_data')


@receiver(post_delete, sender=Customer)
@receiver(post_save, sender=Customer)
@receiver(post_delete, sender=Gem)
@receiver(post_save, sender=Gem)
@receiver(post_delete, sender=DealV2)
@receiver(post_save, sender=DealV2)
def clear_cache(sender, **kwargs):
    """Очистка кэша в случае изменений в таблицах"""
    cache.delete('response_data_ver2')