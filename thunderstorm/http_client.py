import collections
from urllib.parse import urlparse

import requests


DEFAULT_SESSION_POOL_SIZE = 10
DEFAULT_TIMEOUT = 5
DEFAULT_BACKOFF_FACTOR = 0.3
DEFAULT_MAX_TRIES = 3

STATUS_FORCELIST = (500, 502, 504)

KEY_TIMEOUT = "timeout"
KEY_MAX_TRIES = "max_tries"


class SessionPool(collections.OrderedDict):
    def __init__(self, max_size=128, *args, **kwds):
        self.max_size = max_size
        super().__init__(*args, **kwds)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.max_size:
            oldest = next(iter(self))
            oldest.close()
            del self[oldest]


class HttpClient:
    """ Non thread-safety HTTP client
    """
    def __init__(self, session_size=DEFAULT_SESSION_POOL_SIZE, logger=None):
        self.sessions = SessionPool(max_size=session_size)
        self.logger = logger

    def _get_session(self, url):
        host = urlparse(url).netloc
        session = self.sessions.get(host)
        if session is None:
            session = self._new_session()
            self.sessions[host] = session
        return session

    def _new_session(self):
        session = requests.Session()
        return session

    def _log(self, ex):
        if ex is None:
            return

        if self.logger is not None:
            self.logger.error(ex)
        else:
            print(ex)

    def _request_with_session(self, session, method, url, max_tries, **kwargs):
        while max_tries > 0:
            max_tries -= 1
            ex = None
            try:
                r = session.request(method, url, **kwargs)
                if r.status_code in STATUS_FORCELIST:
                    r.raise_for_status()
                return r
            except requests.exceptions.HTTPError as errh:
                ex = errh
            except requests.exceptions.ConnectionError as errc:
                ex = errc
            except requests.exceptions.Timeout as errt:
                ex = errt
            except requests.exceptions.RequestException as err:
                ex = err
            finally:
                self._log(ex)
        raise ex

    def _request(self, method, url, **kwargs):
        if KEY_TIMEOUT not in kwargs:
            kwargs[KEY_TIMEOUT] = DEFAULT_TIMEOUT

        max_tries = DEFAULT_MAX_TRIES
        if KEY_MAX_TRIES in kwargs:
            max_tries = kwargs.pop(KEY_MAX_TRIES)

        max_tries = max_tries if max_tries > 0 else 1
        session = self._get_session(url)
        return self._request_with_session(session, method, url, max_tries, **kwargs)

    def get(self, url, params=None, **kwargs):
        r"""Sends a GET request.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return self._request("GET", url, params=params, **kwargs)

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
        return self._request("POST", url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        r"""Sends a PUT request.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return self._request("PUT", url, data=data, **kwargs)

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
        return self._request("PATCH", url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        r"""Sends a DELETE request.
        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return self._request("DELETE", url, **kwargs)
