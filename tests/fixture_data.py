import pytest


@pytest.fixture
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
