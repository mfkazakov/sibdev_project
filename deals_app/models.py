from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Deal(models.Model):
    """Сервис реализован через одну таблицу, подробнее в README"""
    customer = models.CharField(max_length=255, verbose_name='Логин покупателя')
    item = models.CharField(max_length=255, verbose_name='Наименование товара')
    total = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000000000000)],
                                        verbose_name='Сумма сделки')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000000000000)],
                                           verbose_name='Количество товара,шт')
    date_time = models.DateTimeField(verbose_name='Дата и время регистрации сделки')

    def __str__(self):
        return f'{self.customer} - {self.item} - {self.total}'


