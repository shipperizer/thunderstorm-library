import queue

import requests
import pytest

from thunderstorm.http_client import (SessionPool, HttpClient)


def test_session_pool():
    pool = SessionPool(2)

    session = pool.get()
    assert isinstance(session, requests.Session)

    _ = pool.get()

    with pytest.raises(queue.Empty):
        _ = pool.get(False)


def test_http_client():
    http_client = HttpClient(1)
    assert http_client.sessions.size() == 1

    url = "http://httpbin.org/status/200"
    r = http_client.get(url)
    assert r.status_code == 200

    url = "http://httpbin.org/delay/2"
    with pytest.raises(requests.exceptions.Timeout):
        http_client.get(url, timeout=1)

    assert http_client.sessions.size() == 1


def test_http_client_with_multi_urls():
    http_client = HttpClient(1)
    urls = [
        "https://www.baidu.com",
        "https://www.qq.com",
        "https://www.taobao.com",
    ]
    for url in urls:
        assert http_client.get(url).status_code == 200
