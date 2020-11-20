import csv
import datetime as dt
import json
import os

from loguru import logger


class ParsingJSON:
    """
    После выгрузки из CRM получаем json-файл в виде списка словарей.
    Проходим циклом по списку, достаем из словаря на каждой итерации ключи и
    значения и пересобираем новый список словарей, но уже с заданными ключами.
    Далее, используя csv.DictWriter, собираем из этого списка *.tsv файл
    """

    CONFIG = {
        'TIME_FORMAT': '%Y-%m-%d %H:%M:%S',
        'WEEK_OFFSET': dt.timedelta(hours=24 + 24 + 6),
        'CITY_FIELD_ID': 512318,
        'DRUPAL_UTM_FIELD_ID': 632884,
        'TILDA_UTM_SOURCE_FIELD_ID': 648158,
        'TILDA_UTM_MEDIUM_FIELD_ID': 648160,
        'TILDA_UTM_CAMPAIGN_FIELD_ID': 648310,
        'TILDA_UTM_CONTENT_FIELD_ID': 648312,
        'TILDA_UTM_TERM_FIELD_ID': 648314,
        'CT_UTM_SOURCE_FIELD_ID': 648256,
        'CT_UTM_MEDIUM_FIELD_ID': 648258,
        'CT_UTM_CAMPAIGN_FIELD_ID': 648260,
        'CT_UTM_CONTENT_FIELD_ID': 648262,
        'CT_UTM_TERM_FIELD_ID': 648264,
        'CT_TYPE_COMMUNICATION_FIELD_ID': 648220,
        'CT_DEVICE_FIELD_ID': 648276,
        'CT_OS_FIELD_ID': 648278,
        'CT_BROWSER_FIELD_ID': 648280,
    }

    def __init__(self, config=None):
        self.CONFIG = {}
        if config:
            self.CONFIG.update(config)
        else:
            self.CONFIG.update(ParsingJSON.CONFIG)
        self.final_data = []

    def extract(self, json_file_name):
        """Считывает исходный json-файл."""
        with open(json_file_name, 'r') as json_file:
            self.json_file = json.load(json_file)

    def transform(self):
        """Формирует финальный набор данных для выгрузки в *.tsv."""
        if self.json_file:
            for row in self.json_file:
                self.final_data.append(self.transform_row(row))

    def transform_row(self, source_row):
        """Выбирает ключи и значения из текущих словарей
        и составляет словарь с нужными ключами для одного ряда."""
        custom_field_values = self._get_custom_field_value_by_id(source_row)
        created_at_datetime = dt.datetime.fromtimestamp(
            source_row['created_at']
        )

        result_row = {
            'id': source_row['id'],
            'created_at': source_row['created_at'],
            'amo_updated_at': source_row.get('updated_at'),
            'amo_trashed_at': source_row.get('trashed_at'),
            'amo_closed_at': source_row.get('closed_at'),
            'amo_status_id': source_row['status_id'],
            'amo_pipeline_id': source_row['pipeline_id'],
            'amo_city': custom_field_values.get(self.CONFIG['CITY_FIELD_ID']),
            'drupal_utm': custom_field_values.get(
                self.CONFIG['DRUPAL_UTM_FIELD_ID']
            ),
            'tilda_utm_source': custom_field_values.get(
                self.CONFIG['TILDA_UTM_SOURCE_FIELD_ID']
            ),
            'tilda_utm_medium': custom_field_values.get(
                self.CONFIG['TILDA_UTM_MEDIUM_FIELD_ID']
            ),
            'tilda_utm_campaign': custom_field_values.get(
                self.CONFIG['TILDA_UTM_CAMPAIGN_FIELD_ID']
            ),
            'tilda_utm_content': custom_field_values.get(
                self.CONFIG['TILDA_UTM_CONTENT_FIELD_ID']
            ),
            'tilda_utm_term': custom_field_values.get(
                self.CONFIG['TILDA_UTM_TERM_FIELD_ID']
            ),
            'ct_utm_source': custom_field_values.get(
                self.CONFIG['CT_UTM_SOURCE_FIELD_ID']
            ),
            'ct_utm_medium': custom_field_values.get(
                self.CONFIG['CT_UTM_MEDIUM_FIELD_ID']
            ),
            'ct_utm_campaign': custom_field_values.get(
                self.CONFIG['CT_UTM_CAMPAIGN_FIELD_ID']
            ),
            'ct_utm_content': custom_field_values.get(
                self.CONFIG['CT_UTM_CONTENT_FIELD_ID']
            ),
            'ct_utm_term': custom_field_values.get(
                self.CONFIG['CT_UTM_TERM_FIELD_ID']
            ),
            'ct_type_communication': custom_field_values.get(
                self.CONFIG['CT_TYPE_COMMUNICATION_FIELD_ID']
            ),
            'ct_device': custom_field_values.get(
                self.CONFIG['CT_DEVICE_FIELD_ID']
            ),
            'ct_os': custom_field_values.get(self.CONFIG['CT_OS_FIELD_ID']),
            'ct_browser': custom_field_values.get(
                self.CONFIG['CT_BROWSER_FIELD_ID']
            ),
            'created_at_bq_timestamp': created_at_datetime.strftime(
                self.CONFIG['TIME_FORMAT']
            ),
            'created_at_year': created_at_datetime.year,
            'created_at_month': created_at_datetime.month,
            'created_at_week': (
                (
                    created_at_datetime + self.CONFIG['WEEK_OFFSET']
                ).isocalendar()[1]
            ),
        }
        result_row_add = {
            'lead_utm_source': self._get_lead_utm(result_row, 'source'),
            'lead_utm_medium': self._get_lead_utm(result_row, 'medium'),
            'lead_utm_campaign': self._get_lead_utm(result_row, 'campaign'),
            'lead_utm_content': self._get_lead_utm(result_row, 'content'),
            'lead_utm_term': self._get_lead_utm(result_row, 'keyword'),
        }
        self._check_utm(result_row, result_row_add)
        result_row.update(result_row_add)
        return result_row

    def _get_custom_field_value_by_id(self, source_row):
        """Подготавливает словарь из кастомных id и соответствующих
        им значений.

        По логике предполагается многократный поиск элемента в списке
        source_row. Чтобы уменьшить сложность операции, при первом проходе
        по списку собираем словарь. И в дальнейшем ведем поиск по словарю
        за константное время."""
        if 'custom_fields_values' in source_row:
            custom_fields_dict = {}
            for field in source_row['custom_fields_values']:
                custom_fields_dict[field['field_id']] = field['values'][0].get(
                    'value'
                )
        return custom_fields_dict

    def _get_lead_utm(self, result_row, param):
        """Добавляет колонки, полученные при парсинге
        utm-меток (ключ drupal_utm).
        """
        if result_row['drupal_utm']:
            drupal_utm_list = result_row['drupal_utm'].split(', ')
            drupal_utm_dict = dict(
                [item.split('=') for item in drupal_utm_list]
            )

            source = drupal_utm_dict.get('source')
            medium = drupal_utm_dict.get('medium')
            if param == 'keyword':
                ct_key = 'ct_utm_term'
                tilda_key = 'tilda_utm_term'
            else:
                ct_key = 'ct_utm_' + param
                tilda_key = 'tilda_utm_' + param

            if param not in drupal_utm_dict:
                if result_row[ct_key]:
                    return result_row[ct_key]
                return result_row[tilda_key]

            if param == 'source':
                if source == 'yandex' or medium == 'yandex':
                    return 'yandex'
                if source == 'google' or medium == 'google':
                    return 'google'

            if param == 'medium':
                if source == 'context' or medium == 'context':
                    return 'context'

            return drupal_utm_dict[param]

    def _check_utm(self, result_row, result_row_add):

        for key in result_row_add.keys():
            param = key.split('_')[2]
            ct_key = 'ct_utm_' + param
            tilda_key = 'tilda_utm_' + param
            if (
                result_row[ct_key]
                and (result_row[ct_key] != result_row_add[key])
            ) or (
                result_row[tilda_key]
                and (result_row[tilda_key] != result_row_add[key])
            ):
                self._logger(
                    f"Конфликт {'utm_' + param} в сделке {result_row['id']}"
                )

    def _logger(self, message):
        """Ведёт лог ошибок парсинга utm-меток."""
        logger.add('info.log')
        logger.info(message)

    def load(self, tsv_file_name):
        """Выгружает датафрейм в *.tsv файл."""
        tsv_columns = self.final_data[0].keys()
        with open(tsv_file_name, 'w') as tsvfile:
            writer = csv.DictWriter(
                tsvfile, fieldnames=tsv_columns, dialect='excel-tab'
            )
            writer.writeheader()
            for data in self.final_data:
                writer.writerow(data)


if __name__ == "__main__":
    dirname = os.path.dirname(os.path.abspath(__file__))
    json_file_name = os.path.join(dirname, 'tests', 'amo_json_2020_40.json')
    tsv_file_name = os.path.join(dirname, 'final_table.tsv')

    a = ParsingJSON()
    a.extract(json_file_name)
    a.transform()
    a.load(tsv_file_name)
