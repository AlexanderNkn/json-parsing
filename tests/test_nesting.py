from parsing import ParsingJSON


def test_custom_id(dct):
    """
    Тестирование корректности получения значений из вложенных
    словарей с кастомными id.

    В config даны пары 'название колонки': кастомный_id. В json-e есть
    словари, у которых значения field_id совпадают с кастомным_id. У таких
    словарей нужно взять значение для ключа values. Тест проверяет, что в
    итоговой колонке будет значение ключа values.
    """
    test_config = {
        'custom_id': {
            'column_name_1': 100,
            'column_name_3': 300,
            'column_name_2': 200
        }
    }
    inst = ParsingJSON(test_config)
    key_values = inst._get_values_for_custom_id(dct)
    assert key_values['column_name_1'] == '111', \
        'Значение ключа values не соответствует названию колонки для кастомного id'  # noqa
    column_names = list(key_values.keys())
    assert column_names == ['column_name_1', 'column_name_3', 'column_name_2'], \
        'Порядок названий колонок не соответствует появлению названий в config'  # noqa
