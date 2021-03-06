import braintree
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from orders.models import Order
from .tasks import payment_complete

# Create your views here.

# utworzenie egzemplarza bramki platnosci braintree
gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)


def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # pobranie tokena nonce
        nonce = request.POST.get('payment_method_nonce', None)
        # utworzenie i przeslanie transakcji
        result = gateway.transaction.sale({
            'amount': '{:.2f}'.format(order.get_total_cost()),
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        if result.is_success:
            # oznaczenie jako oplacone
            order.paid = True
            # zapisanie nowego identyfikatora transakcji
            order.braintree_id = result.transaction.id
            order.save()
            # uruchomienie asynchronicznego zadania
            payment_complete.delay(order.id)
            return redirect('payment:done')
        else:
            return redirect('payment:canceled')
    else:
        # wygenerowanie tokenu
        client_token = gateway.client_token.generate()
        return render(request,
                      'payment/process.html',
                      {'order': order,
                       'client_token': client_token})


def payment_done(request):
    return render(request, 'payment/done.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')
