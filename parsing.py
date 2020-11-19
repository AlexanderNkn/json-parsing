import csv
import datetime as dt
import json
import os

from loguru import logger

from weeknum import CustomizedCalendar


class ParsingJSON:
    """
    После выгрузки из CRM получаем json-файл в виде списка словарей.
    Проходим циклом по списку, достаем из словаря на каждой итерации ключи и
    значения и пересобираем новый список словарей, но уже с заданными ключами.
    Далее, используя csv.DictWriter, собираем из этого списка *.tsv файл
    """

    CONFIG = {
        'time_format': '%Y-%m-%d %H:%M:%S',
        'start_week': 'ПТ 18:00',
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

    def __init__(self, config=None):
        self.CONFIG = {}
        if config:
            self.CONFIG.update(config)
        else:
            self.CONFIG.update(ParsingJSON.CONFIG)
        self.final_dict_data = []

    def extract(self, json_file_name):
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
        final_dict_row.update(self._add_datetime_columns(dct))
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
        словаря со словарем 'custom_id' в config, сохранив при этом
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
        # указанные в 'custom_id' в config с сохранением порядка
        add_to_final_dict_row = {}
        for key, val in self.CONFIG['custom_id'].items():
            add_to_final_dict_row[key] = nested_dict.get(val)
        return add_to_final_dict_row

    def _add_datetime_columns(self, dct):
        """Добавляет колонки, вычисляемые из даты."""
        created_at = dct.get('created_at')
        full_date = dt.datetime.fromtimestamp(created_at)
        time_format = self.CONFIG['time_format']
        return {
            'created_at_bq_timestamp': full_date.strftime(time_format),
            'created_at_year': full_date.year,
            'created_a_month': full_date.month,
            'created_at_week': self._weeknum(full_date),
        }

    def _weeknum(self, date):
        """Высчитывает номер недели для недель с нестандартным началом."""
        start_week = self.CONFIG.get('start_week', 'ПТ 18:00')
        inst = CustomizedCalendar(start_week)
        return inst.calculate(date)

    def _get_utm(self, dct):
        """Добавляет колонки, полученные при парсинге
        utm-меток (ключ drupal_utm).
        """
        message = 'привет'
        self._logger(message)
        pass

    def _logger(self, message):
        """Ведёт лог ошибок парсинга utm-меток."""
        logger.add('info.log')
        logger.info(message)

    def load(self, tsv_file_name):
        """Выгружает датафрейм в *.tsv файл."""
        tsv_columns = self.final_dict_data[0].keys()
        with open(tsv_file_name, 'w') as tsvfile:
            writer = csv.DictWriter(
                tsvfile, fieldnames=tsv_columns, dialect='excel-tab'
            )
            writer.writeheader()
            for data in self.final_dict_data:
                writer.writerow(data)


if __name__ == "__main__":
    dirname = os.path.dirname(os.path.abspath(__file__))
    json_file_name = os.path.join(dirname, 'amo_json_2020_40.json')
    tsv_file_name = os.path.join(dirname, 'final_table.tsv')

    a = ParsingJSON()
    a.extract(json_file_name)
    a.transform()
    a.load(tsv_file_name)
