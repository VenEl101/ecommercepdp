
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment


@receiver(post_save, sender=Payment)
def update_order_status(sender, instance, **kwargs):

    order = instance.order

    if instance.status == 'completed' and order.status == 'P':
        order.status = 'A'
        order.save()