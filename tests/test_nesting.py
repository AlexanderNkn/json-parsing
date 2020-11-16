from parsing import ParsingJSON


def test_custom_id(dct):
    """
    Тестирование корректности получения значений из вложенных
    словарей с кастомными id.

    В init_settings даны пары 'название колонки': кастомный_id. В json-e есть
    словари, у которых значения field_id совпадают с кастомным_id. У таких
    словарей нужно взять значение для ключа values. Тест проверяет, что в
    итоговой колонке будет значение ключа values.
    """
    init_settings = {
        'custom_id': {
            'column_name_1': 100,
            'column_name_2': 200,
            'column_name_3': 300
        }
    }
    inst = ParsingJSON(init_settings=init_settings)
    key_values = inst._get_values_for_custom_id(dct)
    assert key_values['column_name_1'] == '111'
