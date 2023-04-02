Для запуска сервиса на MasOS: 

    DOCKER_DEFAULT_PLATFORM=linux/amd64 docker-compose up

Эндпоинты:
    
127.0.0.1:8000/api/upload/ - загрузка данных из файла
    
    POST: Загрузка файла
    Поля:
    - File upload - файл с расширением `.csv` Пример файла находится в корне директории (deals.csv)

Выходные данные:
```json
{
  "Status": "OK"
}
```
либо
```json
{
    "Status": "Error",
    "Desc": <Описание ошибки>
}

```

127.0.0.1:8000/api/best/

    GET: Список из 5 клиентов потративших наибольшую сумму

Поля клиента:

    username-логин клиента;
    spent_money-сумма потраченных средств за весь период;
    gems - список из названий камней, которые купили как минимум двое из списка "5 клиентов, 
        потративших наибольшую сумму за весь период", и данный клиент является одним из этих покупателей.

Выходные данные:
```json
{
    "response": [
        {
            "username": "resplendent",
            "spent_money": 451731,
            "gems": [
                "Рубин",
                "Сапфир",
                "Танзанит"
            ]
        },
      ...
        {
            "username": "turophile",
            "spent_money": 100132,
            "gems": [
                "Изумруд",
                "Рубин"
            ]
        }
    ]
}
```

Дополнительно:
Структуру БД можно было реализовать через связь many-to-many с дополнительными полями. 
Пример кода:
```Python 
from django.db import models

class Customer(models.Model):
    username = models.CharField(max_length=255)


class Gem(models.Model):
    name = models.CharField(max_length=128)
    customers = models.ManyToManyField(Customer, through='Deal')


class Deal(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    gem = models.ForeignKey(Gem, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    date_time = models.DateTimeField()
    
```

Мною было принято решение реализовать через одну таблицу Deal из-за скорости как разработки, так и работы сервиса.