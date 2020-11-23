import csv
import datetime as dt
import json
import os

from loguru import logger

logger.add('info.log', format='{time} {level} {message}', level='INFO')


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
        'ITEMS_2019_FIELD_ID': 648028,
        'ITEMS_2020_FIELD_ID': 562024,
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

    def extract(self, json_file_name):
        """Считывает исходный json-файл."""
        with open(json_file_name, 'r') as json_file:
            return json.load(json_file)

    def transform(self, source_data):
        """Формирует финальный набор данных для выгрузки в *.tsv."""
        result_rows = []
        for row in source_data:
            result_rows.append(self.transform_row(row))
        return result_rows

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
            'amo_items_2019': custom_field_values.get(
                self.CONFIG['ITEMS_2019_FIELD_ID']
            ),
            'amo_items_2020': custom_field_values.get(
                self.CONFIG['ITEMS_2020_FIELD_ID']
            ),
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
        custom_fields_dict = {}
        if source_row.get('custom_fields_values'):
            for field in source_row.get('custom_fields_values'):
                custom_fields_dict[field['field_id']] = field['values'][0].get(
                    'value')
        return custom_fields_dict

    def _get_lead_utm(self, result_row, param):
        """Добавляет колонки, полученные при парсинге
        utm-меток (ключ drupal_utm).
        """
        if param == 'keyword':
            ct_key = 'ct_utm_term'
            tilda_key = 'tilda_utm_term'
        else:
            ct_key = 'ct_utm_' + param
            tilda_key = 'tilda_utm_' + param

        if result_row['drupal_utm']:
            drupal_utm_list = result_row['drupal_utm'].split(', ')
            drupal_utm_dict = dict(
                [item.split('=') for item in drupal_utm_list]
            )

            source = drupal_utm_dict.get('source')
            medium = drupal_utm_dict.get('medium')

            if param not in drupal_utm_dict:
                if result_row[ct_key]:
                    return result_row[ct_key]

            if param == 'source':
                if source == 'yandex' or medium == 'yandex':
                    return 'yandex'
                if source == 'google' or medium == 'google':
                    return 'google'

            if param == 'medium':
                if source == 'context' or medium == 'context':
                    return 'context'

            return drupal_utm_dict[param]
        return result_row[tilda_key]

    def _check_utm(self, result_row, result_row_add):
        for key in result_row_add.keys():
            ct_key = key.replace('lead', 'ct')
            tilda_key = key.replace('lead', 'tilda')
            if (
                result_row[ct_key]
                and (result_row[ct_key] != result_row_add[key])
            ) or (
                result_row[tilda_key]
                and (result_row[tilda_key] != result_row_add[key])
            ):
                logger.info(
                    f"Конфликт {key.replace('lead_', '')} в сделке {result_row['id']}"  # noqa
                )

    def load(self, result_rows, tsv_file_name):
        """Выгружает датафрейм в *.tsv файл."""
        tsv_columns = result_rows[0].keys()
        with open(tsv_file_name, 'w') as tsvfile:
            writer = csv.DictWriter(
                tsvfile, fieldnames=tsv_columns, dialect='excel-tab'
            )
            writer.writeheader()
            for data in result_rows:
                writer.writerow(data)


if __name__ == "__main__":
    dirname = os.path.dirname(os.path.abspath(__file__))
    json_file_name = os.path.join(dirname, 'tests', 'amo_json_2020_40.json')
    tsv_file_name = os.path.join(dirname, 'final_table.tsv')

    week_parser = ParsingJSON()
    source_data = week_parser.extract(json_file_name)
    result_rows = week_parser.transform(source_data)
    week_parser.load(result_rows, tsv_file_name)
