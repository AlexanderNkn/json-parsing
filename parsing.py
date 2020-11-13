import os
import csv
import json


dirname = os.path.dirname(os.path.abspath(__file__))
json_file_name = os.path.join(dirname, 'amo_json_2020_40.json')
tsv_file_name = os.path.join(dirname, 'final_table.tsv')

# TODO !предусмотреть возможность импорта исходных настроек
# в том числе в виде пустого словаря.
initial_settings = {
    # data_format = None  # выбор формата даты
    # start_week = None  # смещение начала недели
    # дальше кастомные id
    'amo_city_id': 512318,
    'drupal_utm': 632884,
    'tilda_utm_source': 648158
    # TODO дописать остальные id
}

class ParsingJSON:
    """
    После выгрузки из CRM получаем json-файл в виде списка словарей.
    Проходим циклом по списку, достаем из словаря на каждой итерации ключи и
    значения и собираем новый словарь в виде
    {
        key1: [value11, value12, value13,...],
        key2: [value21, value22, value23,...],
        ...
    }
    , где key - заданные в бизнес-логике названия полей(колонок)
    """
    def __init__(self):
        self.initial_settings = initial_settings
        self.json_file = None
        self.final_dict = {}

    def extract(self):
        """Считывает исходный json-файл."""
        pass

    def transform(self):
        """Формирует финальный словарь с нужными ключами."""
        pass

    def _transform_row(self):
        """Выбирает ключи и значения из текущих словарей
        и добавляет их в финальный."""
        pass

    def load(self):
        """Выгружает словарь в *.tsv файл."""
        pass
