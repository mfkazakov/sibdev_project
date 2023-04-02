from dataclasses import dataclass
from rest_framework.serializers import ValidationError
import csv
import io
from datetime import datetime
from django.utils.timezone import make_aware


@dataclass
class ParseResult:
    customer: str
    item: str
    total: int
    quantity: int
    date_time: datetime

    def __str__(self):
        return f'ParseResult(customer - {self.customer}, item - {self.item},' \
               f' total - {str(self.total)}, quantity - {str(self.quantity)}, date_time - {str(self.date_time)})'


class DefaultParserFile:
    """
    Стандартный парсер из csv файла
    """
    def __init__(self, file):
        self.file = file

    def parse_file(self) -> list:

        try:
            decoded_file = self.file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string, quotechar='|')
        except Exception as e:
            raise ValidationError({'Status': 'Error', 'Desc': f'Wrong file - {str(e)}'
                                                              f' - в процессе обработки файла произошла ошибка'})

        result = []

        for i, line in enumerate(reader):
            if i == 0:
                continue
            try:
                result.append(ParseResult(
                    customer=line[0],
                    item=line[1],
                    total=int(line[2]),
                    quantity=int(line[3]),
                    date_time=make_aware(datetime.strptime(line[4], "%Y-%m-%d %H:%M:%S.%f")),
                ))
            except ValueError:
                raise ValidationError({'Status': 'Error', 'Desc': f'Wrong format data(total, quantity or date) in file.'
                                                                  f' Line number - {i + 1} '
                                                                  f'- в процессе обработки файла произошла ошибка'})
            except IndexError:
                raise ValidationError({'Status': 'Error', 'Desc': f'Not enough data in line number - {i + 1}'
                                                                  f' - в процессе обработки файла произошла ошибка'})
            except Exception:
                raise ValidationError({'Status': 'Error', 'Desc': f'Wrong data in line - {i + 1}'
                                                                  f' - в процессе обработки файла произошла ошибка'})

        return result


class DealsFromFile:
    """
    Сделки из загруженного файла
    """
    def __init__(self, file):
        self.parser = DefaultParserFile
        self.file = file

    def get_items(self) -> list:
        data = self.parser(self.file).parse_file()
        format_data = []
        for item in data:
            format_data.append({
                'customer': item.customer,
                'item': item.item,
                'total': item.total,
                'quantity': item.quantity,
                'date_time': item.date_time,
            })
        return format_data

