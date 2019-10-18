import json

import requests
import pytest
import urllib3

from thunderstorm.http_client import (HttpClient)


@pytest.fixture(scope="session")
def urls():
    rv = [
        'https://www.baidu.com' for _ in range(20)
    ]
    return rv


@pytest.fixture(scope="session")
def http_client():
    return HttpClient()


def test_http_client():
    http_client = HttpClient()

    url = "http://httpbin.org/status/200"
    r = http_client.get(url)
    assert r.status == 200

    url = "http://httpbin.org/status/404"
    r = http_client.get(url)
    assert r.status == 404

    url = "http://httpbin.org/delay/2"
    with pytest.raises(urllib3.exceptions.MaxRetryError):
        http_client.get(url, timeout=1)


def test_http_client_reuqest_multi_method():
    http_client = HttpClient()
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
        assert f(url).status == 200


def test_http_client_with_multi_urls():
    urls = [
        "https://www.baidu.com",
        "https://www.qq.com",
        "https://www.taobao.com",
        "https://www.alibaba.com"
    ]
    http_client = HttpClient()
    for url in urls:
        assert http_client.get(url).status == 200


def test_http_client_post_put_method():
    http_client = HttpClient()

    data_payload = "hello, world"
    json_payload = {"hello": "world"}

    for method in ["put", "post"]:
        url = "http://httpbin.org/{}".format(method)
        f = getattr(http_client, method)

        resp = f(url, data=data_payload)
        assert resp.status == 200

        content = json.loads(resp.data)
        assert not content['json']

        resp = f(url, json=json_payload)
        assert resp.status == 200

        content = json.loads(resp.data)
        assert content['json'] == json_payload


def test_http_client_get(benchmark, http_client, urls):
    @benchmark
    def request_mulit_url():
        for url in urls:
            assert http_client.get(url).status == 200


def test_requests_get(benchmark, urls):
    @benchmark
    def request_mulit_url():
        for url in urls:
            assert requests.get(url).status_code == 200
