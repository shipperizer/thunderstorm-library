from queue import Queue
import time

import requests


DEFAULT_SESSION_POOL_SIZE = 20
DEFAULT_TIMEOUT = 5
DEFAULT_BACKOFF_FACTOR = 0.3
DEFAULT_MAX_TRIES = 3
DEFAULT_POOL_TIMEOUT = 5

STATUS_FORCELIST = (500, 502, 504)

KEY_TIMEOUT = "timeout"
KEY_MAX_TRIES = "max_tries"


class SessionPool:
    def __init__(self, max_size):
        self.max_size = max_size
        self.pool = Queue(max_size)

        for _ in range(max_size):
            self.pool.put(requests.Session())

    def get(self, block=True, timeout=None):
        return self.pool.get(block, timeout)

    def put(self, session):
        self.pool.put(session)

    def size(self):
        return self.pool.qsize()


class HttpClient:
    """ Non thread-safety HTTP client
    """
    def __init__(self, session_size=DEFAULT_SESSION_POOL_SIZE, logger=None):
        self.sessions = SessionPool(max_size=session_size)
        self.logger = logger

    def _log(self, ex):
        if ex is None:
            return

        if self.logger is not None:
            self.logger.error(ex)
        else:
            print(ex)

    def _request_with_session(self, session, method, url, max_tries, **kwargs):
        for i in range(max_tries):
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

            if (i + 1) != max_tries:
                time.sleep((i + 1) * DEFAULT_BACKOFF_FACTOR)
        raise ex

    def _request(self, method, url, **kwargs):
        if KEY_TIMEOUT not in kwargs:
            kwargs[KEY_TIMEOUT] = DEFAULT_TIMEOUT

        max_tries = DEFAULT_MAX_TRIES
        if KEY_MAX_TRIES in kwargs:
            max_tries = kwargs.pop(KEY_MAX_TRIES)

        max_tries = max_tries if max_tries > 0 else 1
        session = self.sessions.get(timeout=DEFAULT_POOL_TIMEOUT)

        try:
            resp = self._request_with_session(session, method, url, max_tries, **kwargs)
            self.sessions.put(session)
        except Exception as ex:
            self.sessions.put(session)
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
