import os
import pytest
import json


@pytest.fixture
def week_transformer():
    from parsing import ParsingJSON
    return ParsingJSON()


def test_transform_row(week_transformer):

    with open(os.path.join(os.path.dirname(__file__), 'amo_json_2020_40.json')) as test_file:  # noqa
        data = json.loads(test_file.read())

    source_row = [row for row in data if row['id'] == 26895186][0]

    result_row = week_transformer.transform_row(source_row)

    assert result_row['id'] == 26895186
    assert result_row['amo_city'] == 'Брянск'
