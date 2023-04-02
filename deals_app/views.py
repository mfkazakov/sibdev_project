from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from .services.extract_data_from_file import DealsFromFile
from .serializers import UploadDealsSerializer, DealSerializer
from .models import Deal
from django.db.models import Sum, Count
from django.core.cache import cache


class UploadDealsViewSet(CreateModelMixin, viewsets.ViewSet):
    serializer_class = UploadDealsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'Status': 'Error', 'Desc': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        file_uploaded = request.FILES.get('uploaded_file')

        serializer = DealSerializer(data=DealsFromFile(file_uploaded).get_items(), many=True)

        if not serializer.is_valid():
            errors_final = list(filter(None, serializer.errors))
            return Response({'Status': 'Error', 'Desc': errors_final},
                            status=status.HTTP_400_BAD_REQUEST)

        Deal.objects.all().delete()     # Очистка таблицы сделок. Чтобы старые данные не влиляли.

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response({'Status': 'OK'}, status=status.HTTP_201_CREATED, headers=headers)


class BestCustomersViewSet(viewsets.ViewSet):

    def list(self, request):
        cached_data = cache.get('response_data')
        if cached_data:
            return Response({'response': cached_data},
                            status=status.HTTP_200_OK)

        # топ 5 покупателей по потраченым средствам
        top_customers = Deal.objects.values('customer').annotate(sum_total=Sum('total')).order_by('-sum_total')[:5]

        # Получаем названия камней, которые были куплены двумя и более из top_customers (популярные)
        # Вид в SQL
        # SELECT "deals_app_deals"."item"
        #         FROM "deals_app_deals"
        #         WHERE "deals_app_deals"."customer"
        #         IN (resplendent, bellwether, uvulaperfly117, braggadocio, turophile)
        #         GROUP BY "deals_app_deals"."item"
        #         HAVING COUNT(DISTINCT "deals_app_deals"."customer") >= 2
        gems_from_best_cust = Deal.objects.filter(customer__in=[cust['customer'] for cust in top_customers]) \
            .values('item').annotate(count_customers=Count('customer', distinct=True)) \
            .filter(count_customers__gte=2).values_list('item', flat=True)

        response_data = []
        for cust in top_customers:
            deal = {"username": cust['customer'], "spent_money": cust['sum_total'], "gems": []}
            customer_gems = Deal.objects.filter(customer=cust['customer']).distinct().values_list('item', flat=True)
            for gem in customer_gems:
                if gem in gems_from_best_cust:  # Проверка что данный купленный камень есть в списке популярный камней
                    deal["gems"].append(gem)
            response_data.append(deal)

        cache.set('response_data', response_data, 60 * 15)

        return Response({'response': response_data},
                        status=status.HTTP_200_OK)


