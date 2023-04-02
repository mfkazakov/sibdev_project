from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


'''Реализация через одну таблицу'''


class Deal(models.Model):
    customer = models.CharField(max_length=255, verbose_name='Логин покупателя')
    item = models.CharField(max_length=255, verbose_name='Наименование товара')
    total = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000000000000)],
                                        verbose_name='Сумма сделки')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000000000000)],
                                           verbose_name='Количество товара,шт')
    date_time = models.DateTimeField(verbose_name='Дата и время регистрации сделки')

    def __str__(self):
        return f'{self.customer} - {self.item} - {self.total}'


''' Реализация через связанные таблицы '''


class Customer(models.Model):
    username = models.CharField(max_length=255, verbose_name='Логин покупателя')

    def __str__(self):
        return self.username


class Gem(models.Model):
    item = models.CharField(max_length=255, verbose_name='Наименование товара')

    def __str__(self):
        return self.item


class DealV2(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, related_name='deal')
    gem = models.ForeignKey(Gem, on_delete=models.DO_NOTHING, related_name='deal')
    total = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000000000000)],
                                        verbose_name='Сумма сделки')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000000000000)],
                                           verbose_name='Количество товара,шт')
    date_time = models.DateTimeField(verbose_name='Дата и время регистрации сделки')

    def __str__(self):
        return f'{self.customer.username} - {self.gem.item} - {self.total}'


