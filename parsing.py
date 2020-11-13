import csv
import json
import os


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
        self.initial_settings = initial_settings
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
                self._transform_row(dct)

    def _transform_row(self, dct):
        """Выбирает ключи и значения из текущих словарей
        и составляет список из словарей с нужными ключами."""
        self.final_dict_data.append({
            'id': dct.get('id'),
            'created_at': dct.get('created_at', 0),
            'amo_pipeline_id': dct.get('pipeline_id', 0),
            'amo_status_id': dct.get('status_id', 0),
            'amo_updated_at': dct.get('updated_at', 0),
            'amo_trashed_at': dct.get('trashed_at', 0),
            'amo_closed_at': dct.get('closed_at', 0),
        })
        # TODO 1 оставлять ли None в финальной таблице, или на что-то поменять?
        # TODO 2 дописать ключи от вложенных словарей
        # TODO 3 дописать обработку дат. При смещении старта недели
        # попробовать доработать isocalendar()
        # TODO 4 дописать проверку отсутствующих ключей-значений по заданию
        # TODO 5 дописать логгер для события из TODO 4

    def load(self):
        """Выгружает датафрейм в *.tsv файл."""
        tsv_columns = [
            'id', 'created_at', 'amo_pipeline_id', 'amo_status_id',
            'amo_updated_at', 'amo_trashed_at', 'amo_closed_at',
        ]
        try:
            with open(tsv_file_name, 'w') as tsvfile:
                writer = csv.DictWriter(
                    tsvfile, fieldnames=tsv_columns, dialect='excel-tab')
                writer.writeheader()
                for data in self.final_dict_data:
                    writer.writerow(data)
        except IOError:
            print("OS error")


a = ParsingJSON()
# print(a)
a.extract()
# print(a.json_file)
a.transform()
# print(a.final_dict)
# print(a.final_dict_data)
a.load()
