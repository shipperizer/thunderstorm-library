import json as json_package

import urllib3
from urllib3.util.retry import Retry


DEFAULT_SESSION_POOL_SIZE = 20
DEFAULT_TIMEOUT = 5
DEFAULT_BACKOFF_FACTOR = 0.3
DEFAULT_MAX_TRIES = 3
DEFAULT_POOL_TIMEOUT = 5

STATUS_FORCELIST = (500, 502, 504)

KEY_TIMEOUT = "timeout"
KEY_MAX_TRIES = "max_tries"


class HttpClient:
    """ Non thread-safety HTTP client
    """
    def __init__(self, session_size=DEFAULT_SESSION_POOL_SIZE, logger=None):
        self.pool = urllib3.PoolManager(num_pools=session_size)
        self.logger = logger

    def _log(self, ex):
        if ex is None:
            return

        if self.logger is not None:
            self.logger.error(ex)
        else:
            print(ex)

    def _request(self, method, url, **kwargs):
        if KEY_TIMEOUT not in kwargs:
            kwargs[KEY_TIMEOUT] = DEFAULT_TIMEOUT

        max_tries = DEFAULT_MAX_TRIES
        if KEY_MAX_TRIES in kwargs:
            max_tries = kwargs.pop(KEY_MAX_TRIES)

        max_tries = max_tries if max_tries > 0 else 1
        if max_tries > 1:
            kwargs['retries'] = Retry(
                total=max_tries,
                status_forcelist=STATUS_FORCELIST,
                backoff_factor=DEFAULT_BACKOFF_FACTOR
            )
        else:
            kwargs['retries'] = False

        try:
            resp = self.pool.request(method, url, **kwargs)
        except Exception as ex:
            raise ex

        return resp

    def get(self, url, params=None, **kwargs):
        r"""Sends a GET request.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return self._request("GET", url, fields=params, **kwargs)

    def options(self, url, **kwargs):
        r"""Sends an OPTIONS request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return self._request("OPTIONS", url, **kwargs)

    def head(self, url, **kwargs):
        r"""Sends a HEAD request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes. If
            `allow_redirects` is not provided, it will be set to `False` (as
            opposed to the default :meth:`request` behavior).
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return self._request("HEAD", url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        r"""Sends a POST request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        if json is not None:
            data = json_package.dumps(json).encode('utf-8')
            headers = kwargs.get('headers', {})
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
            kwargs['headers'] = headers
        return self._request("POST", url, body=data, **kwargs)

    def put(self, url, data=None, json=None, **kwargs):
        r"""Sends a PUT request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        if json is not None:
            data = json_package.dumps(json).encode('utf-8')
            headers = kwargs.get('headers', {})
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
            kwargs['headers'] = headers
        return self._request("PUT", url, body=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        r"""Sends a PATCH request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return self._request("PATCH", url, fields=data, **kwargs)

    def delete(self, url, **kwargs):
        r"""Sends a DELETE request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return self._request("DELETE", url, **kwargs)
