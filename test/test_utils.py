import pytest

from thunderstorm.utils import get_pagination_info


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
