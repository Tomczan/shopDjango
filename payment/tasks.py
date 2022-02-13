from io import BytesIO
from celery import shared_task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order


@shared_task
def payment_complete(order_id):
    '''
    E-mail po pomyslnym utworzeniu zamówienia
    '''
    order = Order.objects.get(id=order_id)
    subject = f'Moj sklep - rachunek nr {order.id}'
    message = 'W załączniku przesyłamy rachunek do ostatniego zakupu.'
    email = EmailMessage(subject,
                         message,
                         'admin@shopDjango.com',
                         [order.email])
    # wygenerowanie PDF
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    # Dolaczenie pliku PDF do maila
    email.attach(f'order_{order.id}', out.getvalue(), 'application/pdf')
    email.send()
