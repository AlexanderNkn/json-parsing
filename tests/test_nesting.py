"""
Тестирование корректности получения значений из вложенных
словарей с кастомными id.
"""
from parsing import ParsingJSON
import pytest


@pytest.fixture()
def dct():
    return {
        "id": 1234,
        "status_id": 1234,
        "pipeline_id": 1234,
        "created_at": 1234,
        "updated_at": 1234,
        "closed_at": 1234,
        "custom_fields_values": [
            {
                "field_id": 100,
                "values": [
                    {"value": "111"},
                ],
            },
            {
                "field_id": 200,
                "values": [
                    {"value": "222"},
                ],
            },
            {
                "field_id": 300,
                "values": [
                    {"value": "333"},
                ],
            },
        ],
        "trashed_at": 1234,
    }

a = dct
print(a)

def test_custom_id():
    inst = ParsingJSON()
    inst._get_values_for_custom_id(dct)
    assert inst.final_dict_data == 1
