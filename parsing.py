# TODO +1 оставлять ли None в финальной таблице или на что-то поменять?
# TODO +2 дописать ключи от вложенных словарей
# TODO тесты
# TODO 3 дописать обработку дат. При смещении старта недели
# попробовать доработать isocalendar()
# TODO 4 дописать отдельную фукцию для drupal_utm
# TODO 4 дописать проверку отсутствующих ключей-значений по заданию
# TODO 5 дописать логгер для события из TODO 4

import csv
import json
import os

# исходные настройки парсера можно импортировать из другого файла,
# для этого нужно назвать их ext_settings и указать путь до файла
try:
    from some.path import ext_settings  # noqa
except ImportError:
    ext_settings = None


dirname = os.path.dirname(os.path.abspath(__file__))
json_file_name = os.path.join(dirname, 'amo_json_2020_40.json')
tsv_file_name = os.path.join(dirname, 'final_table.tsv')
init_settings = {
    'date_format': None,  # выбор формата даты !!! не подключено
    'start_week': None,  # смещение начала недели !!! не подключено
    'custom_id': {
        'amo_city_id': 512318,
        'drupal_utm': 632884,
        'tilda_utm_source': 648158,
        'tilda_utm_source': 648158,
        'tilda_utm_medium': 648160,
        'tilda_utm_campaign': 648310,
        'tilda_utm_content': 648312,
        'tilda_utm_term': 648314,
        'ct_utm_source': 648256,
        'ct_utm_medium': 648258,
        'ct_utm_campaign': 648260,
        'ct_utm_content': 648262,
        'ct_utm_term': 648264,
        'ct_type_communication': 648220,
        'ct_device': 648276,
        'ct_os': 648278,
        'ct_browser': 648280,
    },
}
# Если были импортированы внешние настройки, то они
# перезаписывают дефолтные
init_settings = ext_settings if ext_settings else init_settings


class ParsingJSON:
    """
    После выгрузки из CRM получаем json-файл в виде списка словарей.
    Проходим циклом по списку, достаем из словаря на каждой итерации ключи и
    значения и пересобираем новый список словарей, но уже с заданными ключами.
    Получаем список словарей в таком виде:
    [
        {key11: value11, key12: value12, key13: value13,...},
        {key11: value11, key12: value12, key13: value13,...},
        ...
    ]
    Далее, используя csv.DictWriter, собираем из этого списка *.tsv файл
    """
    def __init__(self):
        self.init_settings = init_settings
        self.json_file = None
        self.final_dict_data = []

    def extract(self):
        """Считывает исходный json-файл."""
        with open(json_file_name, 'r') as json_file:
            self.json_file = json.load(json_file)

    def transform(self):
        """Формирует финальный набор данных для выгрузки в *.tsv."""
        if self.json_file:
            for dct in self.json_file:
                self.final_dict_data.append(self._transform_row(dct))

    def _transform_row(self, dct):
        """Выбирает ключи и значения из текущих словарей
        и составляет словарь с нужными ключами для одного ряда."""
        final_dict_row = self._get_values_for_general_data(dct)
        final_dict_row.update(self._get_values_for_custom_id(dct))
        return final_dict_row

    def _get_values_for_general_data(self, dct):
        """Выбирает из json-a общие данные - id, создан, изменен и т.д."""
        return {
            'id': dct.get('id'),
            'created_at': dct.get('created_at'),
            'amo_pipeline_id': dct.get('pipeline_id'),
            'amo_status_id': dct.get('status_id'),
            'amo_updated_at': dct.get('updated_at'),
            'amo_trashed_at': dct.get('trashed_at'),
            'amo_closed_at': dct.get('closed_at'),
        }

    def _get_values_for_custom_id(self, dct):
        """Выбирает из текущих словарей значения для кастомных id.

        Значение 'custom_fields_values' представляет собой список словарей.
        Так как нам нужно сопоставить только значение 'field_id' из каждого
        словаря со словарем 'custom_id' в init_settings, сохранив при этом
        порядок, создадим промежуточный словарь вида:
        {
            key1: value1,
            key2: value2,
            ...
        }
        ,где key1 - это значения ключа 'field_id', а value1 - это значение для
        ключа 'values' из вложенного словаря, которому принадлежит 'field_id'.
        """
        nested_dict = {}
        custom_fields_list = dct['custom_fields_values']
        for item in custom_fields_list:
            nested_dict[item['field_id']] = item['values'][0]['value']
        # выбираем из временного словаря nested_dict только ключи,
        # указанные в 'custom_id' в init_settings с сохранением порядка
        add_to_final_dict_row = {}
        for key, val in init_settings['custom_id'].items():
            add_to_final_dict_row[key] = nested_dict.get(val)
        return add_to_final_dict_row

    def _add_datetime_columns(self, dct):
        """Добавляет колонки, вычисляемые из даты."""
        pass

    def _get_utm(self, dct):
        """Добавляет колонки, полученные при парсинге
        utm-меток (ключ drupal_utm).
        """
        self._logger()
        pass

    def _logger(self):
        """Ведёт лог ошибок парсинга utm-меток."""
        pass

    def load(self):
        """Выгружает датафрейм в *.tsv файл."""
        tsv_columns = self.final_dict_data[0].keys()
        with open(tsv_file_name, 'w') as tsvfile:
            writer = csv.DictWriter(
                tsvfile, fieldnames=tsv_columns, dialect='excel-tab')
            writer.writeheader()
            for data in self.final_dict_data:
                writer.writerow(data)


a = ParsingJSON()
# print(a)
a.extract()
# print(a.json_file)
a.transform()
# print(a.final_dict)
a.load()
