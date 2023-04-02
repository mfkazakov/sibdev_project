from rest_framework.serializers import Serializer, FileField, ValidationError, ModelSerializer
from .models import Deal


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

