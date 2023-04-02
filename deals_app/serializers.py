from rest_framework.serializers import Serializer, FileField, ValidationError, ModelSerializer
from .models import Deal, DealV2, Gem, Customer
from rest_framework import serializers

class UploadDealsSerializer(Serializer):
    uploaded_file = FileField()

    def validate(self, data):

        if str(data['uploaded_file']).split('.')[-1] != 'csv':
            raise ValidationError(f"Wrong file format ({str(data['uploaded_file']).split('.')[-1]})"
                                  f" - в процессе обработки файла произошла ошибка")
        return data

    class Meta:
        fields = ['uploaded_file']


class DealSerializer(ModelSerializer):

    class Meta:
        model = Deal
        fields = ['customer', 'item', 'total', 'quantity', 'date_time']


''' Реализация через связанные таблицы '''


class CustomerSerializer(ModelSerializer):
    customer = serializers.CharField(source='username')

    class Meta:
        model = Customer
        fields = ['customer']


class GemSerializer(ModelSerializer):

    class Meta:
        model = Gem
        fields = ['item']


class DealV2Serializer(ModelSerializer):
    customer = serializers.CharField(source='customer.pk')
    item = serializers.CharField(source='gem.pk')

    class Meta:
        model = DealV2
        fields = ['customer', 'item', 'total', 'quantity', 'date_time']