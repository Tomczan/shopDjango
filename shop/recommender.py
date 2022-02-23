import redis
from django.conf import settings
from .models import Product

# nawiazanie polaczenia
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


class Recommender(object):

    def get_product_key(self, id):
        return f'product:{id}:purchased_with'

    def products_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # pobranie innych produktow kupionych razem z analizowanym
                if product_id != with_id:
                    r.zincrby(self.get_product_key(product_id),
                              1,
                              with_id)

    def suggest_products_for(self, products, max_results=6):
        product_ids = [p.id for p in products]
        if len(products) == 0:
            return []
        if len(products) == 1:
            # tylko 1 produkt
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]),
                0, -1, desc=True)[:max_results]
        else:
            # wygenerowanie klucza podstawowego
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = f'tmp_{flat_ids}'
            # wiele produktow, sumowanie punktow wszystkich produktow
            # umieszczanie w kluczu tumczasowym posortowanej kolekcji wynikowej
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)
            # usuniecie identyfikatorow produktow, dla ktorych przygotowujemy rekomendacje
            r.zrem(tmp_key, *product_ids)
            # pobranie identyfikatorow produktow wedlug ich punktacji
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            # usuniecie klucza podstawowego
            r.delete(tmp_key)
        suggested_products_ids = [int(id) for id in suggestions]
        # pobrananie sugerowanych produktow i ulozenie ich w kolejnosci pojawiania sie
        suggested_products = list(
            Product.objects.filter(id__in=suggested_products_ids))
        suggested_products.sort(
            key=lambda x: suggested_products_ids.index(x.id))
        return suggested_products

    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))
