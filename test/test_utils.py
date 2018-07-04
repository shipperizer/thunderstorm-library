from unittest.mock import MagicMock

import pytest

from thunderstorm.utils import get_pagination_info, paginate


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
