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

    assert result_row['ct_utm_content'] == '<не заполнено>'
    assert result_row['tilda_utm_content'] is None
    assert result_row['lead_utm_content'] == 'cntx'

    assert 'source=yandex' in result_row['drupal_utm']
    assert result_row['lead_utm_source'] == 'yandex'
