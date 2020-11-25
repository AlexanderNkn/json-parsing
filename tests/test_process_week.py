import json
from pathlib import Path
from unittest import mock

import pytest


@pytest.fixture
def week_transformer():
    from parsing import ParsingJSON
    return ParsingJSON()


@pytest.fixture
def mocked_logger():
    from parsing import logger
    logger.info = mock.MagicMock()
    return logger


def get_test_data(file_name):
    test_file_path = Path(__file__).parent / file_name
    with test_file_path.open() as test_file:
        return json.loads(test_file.read())


def test_lead_utm_field_drupal_utm_yandex_and_search(week_transformer, mocked_logger):
    """Drupal_utm (кастомное поле с field_id=632884) не пустое, и содержит
    source=search, medium=yandex
    """
    test_data = get_test_data('amo_json_2020_04.json')

    source_row = [row for row in test_data if row['id'] == 25827302][0]
    result_row = week_transformer.transform_row(source_row)

    assert mocked_logger.info.call_count == 0
    assert result_row['lead_utm_source'] == 'yandex'
    assert result_row['lead_utm_medium'] == 'search'
    assert result_row['lead_utm_campaign'] == 'green'
    assert result_row['lead_utm_content'] == 'cntx'
    expected = '16679054-1229635987-7566047867--1--none--продвижение_сайтов'
    assert result_row['lead_utm_term'] == expected


def test_lead_utm_field_drupal_utm_google_and_search(week_transformer, mocked_logger):
    """Drupal_utm (кастомное поле с field_id=632884) не пустое, и содержит
    source=search, medium=google
    """
    test_data = get_test_data('amo_json_2020_04.json')

    source_row = [row for row in test_data if row['id'] == 25840730][0]
    result_row = week_transformer.transform_row(source_row)

    assert mocked_logger.info.call_count == 0
    assert result_row['lead_utm_source'] == 'google'
    assert result_row['lead_utm_medium'] == 'search'
    assert result_row['lead_utm_campaign'] == 'green'
    assert result_row['lead_utm_content'] == 'cntx'
    expected = '773449390-39333121183-254178538311--1t2----_яндекс__реклама'
    assert result_row['lead_utm_term'] == expected


def test_lead_utm_field_ct_utm(week_transformer, mocked_logger):
    """Есть поля ct_type_communication и ct_utm_*"""
    test_data = get_test_data('amo_json_2020_40.json')

    source_row = [row for row in test_data if row['id'] == 26895186][0]
    result_row = week_transformer.transform_row(source_row)

    assert mocked_logger.info.call_count == 5
    assert result_row['lead_utm_source'] == 'yandex'
    assert result_row['lead_utm_medium'] == 'search'
    assert result_row['lead_utm_campaign'] == 'green'
    assert result_row['lead_utm_content'] == 'cntx'
    expected = '16678927-1229623120-1711872754--2--none--контекстная_реклама'
    assert result_row['lead_utm_term'] == expected


def test_lead_utm_field_drupal_utm_yandex_and_context(week_transformer, mocked_logger):
    """Drupal_utm (кастомное поле с field_id=632884) не пустое, и содержит
    содержит source=yandex, medium=context
    """
    test_data = get_test_data('amo_json_2020_40.json')

    source_row = [row for row in test_data if row['id'] == 26897900][0]
    result_row = week_transformer.transform_row(source_row)

    assert mocked_logger.info.call_count == 0
    assert result_row['lead_utm_source'] == 'yandex'
    assert result_row['lead_utm_medium'] == 'context'
    assert result_row['lead_utm_campaign'] == '17600'
    assert result_row['lead_utm_content'] == 'web'
    exptd = '46954677-4000555842-8182712256--0--zen.yandex.ru--создание_сайт_под_ключ'
    assert result_row['lead_utm_term'] == exptd


def test_lead_utm_field_drupal_utm_google_and_context(week_transformer, mocked_logger):
    """Drupal_utm (кастомное поле с field_id=632884) не пустое, и содержит
    содержит source=google, medium=context
    """
    test_data = get_test_data('amo_json_2020_40.json')

    source_row = [row for row in test_data if row['id'] == 26887462][0]
    result_row = week_transformer.transform_row(source_row)

    assert mocked_logger.info.call_count == 0
    assert result_row['lead_utm_source'] == 'google'
    assert result_row['lead_utm_medium'] == 'context'
    assert result_row['lead_utm_campaign'] == 'blue'
    assert result_row['lead_utm_content'] == 'cntx'
    expected = '1351759424-77001425413-378733477874--none--doneto.ru--'
    assert result_row['lead_utm_term'] == expected
