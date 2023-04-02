from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from .services.extract_data_from_file import DealsFromFile
from .serializers import UploadDealsSerializer, DealSerializer, DealV2Serializer, GemSerializer, CustomerSerializer
from .models import Deal, DealV2, Customer, Gem
from django.db.models import Sum, Count
from django.core.cache import cache

from collections import Counter


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

        Deal.objects.all().delete()     # Очистка старой таблицы сделок. Чтобы старые данные не влиляли.

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
        gems_from_best_cust = set(Deal.objects.filter(customer__in=[cust['customer'] for cust in top_customers])
                                  .values('item').annotate(count_customers=Count('customer', distinct=True))
                                  .filter(count_customers__gte=2).values_list('item', flat=True))

        response_data = []
        for cust in top_customers:
            deal = {"username": cust['customer'], "spent_money": cust['sum_total'], "gems": []}
            customer_gems = set(Deal.objects.filter(customer=cust['customer']).distinct()
                                .values_list('item', flat=True))
            deal["gems"] = customer_gems & gems_from_best_cust  # Проверка что данный купленный камень есть в списке популярный камней

            response_data.append(deal)

        cache.set('response_data', response_data, 60 * 15)

        return Response({'response': response_data},
                        status=status.HTTP_200_OK)


''' Реализация через связанные таблицы '''


class UploadDealsVer2ViewSet(viewsets.ViewSet):
    serializer_class = UploadDealsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'Status': 'Error', 'Desc': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        DealV2.objects.all().delete()  # Очистка старых таблиц. Чтобы старые данные не влиляли.
        Customer.objects.all().delete()
        Gem.objects.all().delete()

        file_uploaded = request.FILES.get('uploaded_file')

        data_from_file = DealsFromFile(file_uploaded).get_items()

        for data in data_from_file:

            customer_serializer = CustomerSerializer(data=data)
            if not customer_serializer.is_valid():
                return Response({'Status': 'Error', 'Desc': customer_serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

            customer, _ = Customer.objects.get_or_create(username=customer_serializer.validated_data['username'])

            gem_serializer = GemSerializer(data=data)
            if not gem_serializer.is_valid():
                return Response({'Status': 'Error', 'Desc': gem_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            gem, _ = Gem.objects.get_or_create(
                item=gem_serializer.validated_data['item']
            )

            deal_serializer = DealV2Serializer(data=data)
            if not deal_serializer.is_valid():
                return Response({'Status': 'Error', 'Desc': deal_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            DealV2.objects.get_or_create(
                customer=customer,
                gem=gem,
                total=deal_serializer.validated_data['total'],
                quantity=deal_serializer.validated_data['quantity'],
                date_time=deal_serializer.validated_data['date_time'],
            )

        return Response({'Status': 'OK'}, status=status.HTTP_201_CREATED)


class BestCustomersVer2ViewSet(viewsets.ViewSet):

    def list(self, request):
        cached_data = cache.get('response_data_ver2')
        if cached_data:
            return Response({'response': cached_data},
                            status=status.HTTP_200_OK)

        # топ 5 покупателей по потраченым средствам
        top_customers = Customer.objects.annotate(sum_total=Sum('deal__total')).order_by('-sum_total')[:5].\
            prefetch_related('deal')

        customers_gems = {}
        counter = Counter()
        # множества купленных камней для покупателей
        for customer in top_customers:
            customer_gems = set(buf.gem.item for buf in customer.deal.select_related('gem'))
            customers_gems[customer] = customer_gems
            counter += Counter(customer_gems)

        popular_gems = set([gems for gems, frequency in counter.items() if frequency >= 2])

        response_data = []
        for customer in top_customers:
            deal = {
                "username": customer.username,
                "spent_money": customer.sum_total,
                "gems": customers_gems[customer] & popular_gems}
            response_data.append(deal)

        cache.set('response_data_ver2', response_data, 60 * 15)

        return Response({'response': response_data},
                        status=status.HTTP_200_OK)

