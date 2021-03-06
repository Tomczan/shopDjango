from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task
def order_created(order_id):
    """
    Zadanie wysylające maila (lokalnie na konsoli) po zakonczonym powodzeniem utworzenia obiektu zamówienia.
    """
    order = Order.objects.get(id=order_id)
    subject = f'Zamówienie nr {order_id}'
    message = f'Witaj, {order.first_name}, \nZłożyłes zamówienie w naszym sklepie. Id zamówienia to {order.id}'
    mail_sent = send_mail(subject, message, 'admin@shop.com', [order.email])
    return mail_sent
