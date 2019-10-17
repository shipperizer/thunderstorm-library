import queue
import random

import requests
import pytest

from thunderstorm.http_client import (SessionPool, HttpClient)


@pytest.fixture(scope="session")
def urls():
    rv = [
        'https://www.alibaba.com' for _ in range(20)
    ]
    return rv


@pytest.fixture(scope="session")
def http_client():
    return HttpClient()


def test_session_pool():
    pool = SessionPool(2)

    session = pool.get()
    assert isinstance(session, requests.Session)

    pool.get()
    with pytest.raises(queue.Empty):
        pool.get(False)


def test_http_client():
    http_client = HttpClient(1)
    assert http_client.sessions.size() == 1

    url = "http://httpbin.org/status/200"
    r = http_client.get(url)
    assert r.status_code == 200

    url = "http://httpbin.org/status/404"
    r = http_client.get(url)
    assert r.status_code == 404

    url = "http://httpbin.org/delay/2"
    with pytest.raises(requests.exceptions.Timeout):
        http_client.get(url, timeout=1)

    assert http_client.sessions.size() == 1


def test_http_client_reuqest_multi_method():
    http_client = HttpClient(1)
    assert http_client.sessions.size() == 1

    url = "http://httpbin.org/status/200"
    methods = [
        "get",
        "options",
        "head",
        "post",
        "put",
        "patch",
        "delete"
    ]

    for m in methods:
        f = getattr(http_client, m)
        assert f(url).status_code == 200


def test_http_client_with_multi_urls():
    urls = [
        "https://www.baidu.com",
        "https://www.qq.com",
        "https://www.taobao.com",
        "https://www.alibaba.com"
    ]
    http_client = HttpClient(1)
    for url in urls:
        assert http_client.get(url).status_code == 200


def test_http_client_get(benchmark, http_client, urls):
    @benchmark
    def request_mulit_url():
        for url in urls:
            assert http_client.get(url).status_code == 200


def test_requests_get(benchmark, urls):
    @benchmark
    def request_mulit_url():
        for url in urls:
            assert requests.get(url).status_code == 200
