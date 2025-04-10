from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Payment


@receiver(post_save, sender=Payment)
def update_order_status_on_payment(sender, instance, created, **kwargs):
    if created:
        order = instance.order
        order.status = 'P'
        order.save()


