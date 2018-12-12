from unittest.mock import MagicMock

import pytest

from test.helpers import patch_fixture, TestSchema, TestException
from thunderstorm.exceptions import DeserializationError
from thunderstorm.utils import get_pagination_info, paginate, get_request_filters, get_request_pagination

mock_request = patch_fixture('thunderstorm.utils.request')


@pytest.mark.parametrize('page,page_size,num_records,prev_page,next_page,url', [
    (1, 20, 40, None, '/foo/bar?page_size=20&page=2', '/foo/bar',),
    (2, 20, 60, '/foo/bar?page_size=20&page=1', '/foo/bar?page_size=20&page=3', '/foo/bar',),
    (1, 20, 3, None, None, '/foo/bar',),
    (1, 20, 40, None, '/foo/bar?page_size=20&page=2', '/foo/bar',),
    (1, 20, 40, None, '/foo/bar?page_size=20&page=2', '/foo/bar',),
    (1, 20, 40, None, '/foo/bar?page_size=20&page=2', '/foo/bar?page_size=1000&page=50',),
])
def test_get_pagination_info(page, page_size, num_records, prev_page, next_page, url):
    res = get_pagination_info(page, page_size, num_records, url)
    assert res.get('prev_page') == prev_page
    assert res.get('next_page') == next_page
    assert res['total_records'] == num_records


@pytest.mark.parametrize('page,page_size,num_records,prev_page,next_page,url', [
    (1, 20, 40, None, '/foo/bar?page_size=20&page=2', '/foo/bar',),
    (2, 20, 60, '/foo/bar?page_size=20&page=1', '/foo/bar?page_size=20&page=3', '/foo/bar',),
    (2, 20, 60, '/foo/bar?id=5&jezoo=ovp&page_size=20&page=1', '/foo/bar?id=5&jezoo=ovp&page_size=20&page=3', '/foo/bar?id=5&jezoo=ovp',),
    (1, 20, 3, None, None, '/foo/bar',),
    (1, 20, 40, None, '/foo/bar?page_size=20&page=2', '/foo/bar',),
    (1, 20, 40, None, '/foo/bar?page_size=20&page=2', '/foo/bar',),
    (1, 20, 40, None, '/foo/bar?page_size=20&page=2', '/foo/bar?page_size=1000&page=50',),
])
def test_paginate(page, page_size, num_records, prev_page, next_page, url):
    m_query = MagicMock()
    m_query.offset.return_value = m_query
    m_query.limit.return_value = m_query
    m_query.count.return_value = num_records

    res_query, res_page_info = paginate(m_query, page, page_size, url)

    assert res_page_info.get('prev_page') == prev_page
    assert res_page_info.get('next_page') == next_page
    assert res_page_info['total_records'] == num_records

    res_query.offset.assert_called_with((page - 1) * page_size)
    res_query.limit.assert_called_with(page_size)
    assert res_query == m_query


def test_get_request_filters_raises_with_bad_data(mock_request):
    # arrange
    data = {'int_1': 'notinteger', 'int_2': 2}
    mock_request.args = data

    # act/assert
    with pytest.raises(TestException):
        get_request_filters(TestSchema, TestException)


def test_get_request_filters_success(mock_request):
    # arrange
    data = {'int_1': 1, 'int_2': 2}
    mock_request.args = data

    # act/assert
    assert get_request_filters(TestSchema, TestException) == {'int_1': 1, 'int_2': 2}


def test_get_request_pagination_success_with_dict():
    # arrange
    data = {'page': 1, 'page_size': 2}

    # act/assert
    assert get_request_pagination(data) == {'page': 1, 'page_size': 2}


def test_get_request_pagination_failure_raises_KeyError_with_missing_key():
    # arrange
    data = {'page': 1, 'wrong': 2}

    # act/assert
    with pytest.raises(KeyError):
        assert get_request_pagination(data)


def test_get_request_pagination_raises_exc_when_provided_and_request_args_invalid(mock_request):
    # arrange
    data = {'page': 1, 'page_size': 'word'}
    mock_request.args = data

    # act/assert
    with pytest.raises(TestException):
        get_request_pagination(exc=TestException)


def test_get_request_pagination_raises_DeserializationError_when_no_exc_provided_and_request_args_invalid(mock_request):
    # arrange
    data = {'page': 1, 'page_size': 'word'}
    mock_request.args = data

    # act/assert
    with pytest.raises(DeserializationError):
        get_request_pagination()


def test_get_request_pagination_success_with_request_args(mock_request):
    # arrange
    data = {'page': 1, 'page_size': 1}
    mock_request.args = data

    # act/assert
    assert get_request_pagination(exc=TestException) == data
