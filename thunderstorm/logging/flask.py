"""Module for integrating logging with Flask

Usage:
    >>> from flask import Flask
    >>> from thunderstorm.logging.flask import init_app as init_logging
    >>>
    >>> app = Flask(__init__)
    >>> init_logging(app)
"""
import logging
from flask import g, request, Flask
from flask.ctx import has_request_context

from . import (
    _register_id_getter, get_log_level, get_request_id,
    ts_stream_handler, setup_root_logger, TS_REQUEST_ID
)

__all__ = ['init_app']


class FlaskRequestIDFilter(logging.Filter):
    def filter(self, record):
        record.traceId = get_request_id()

        return record


def get_flask_request_id():
    """Return the request ID from the Flask request context

    If there is a Flask request context but there is no ``request_id``
    then first we look for a ``TS-Request-ID`` header. If that is also
    not there we generate a new string uuid4.

    Importing this module will register this getter with ``get_request_id``.

    Returns:
        str: the current request ID
    """
    if has_request_context():
        if TS_REQUEST_ID in request.headers:
            return request.headers[TS_REQUEST_ID]

        if 'request_id' in g:
            return g.request_id

    return None


def init_app(app: Flask):
    """Initialise logging request handler on a Flask app
    This handler adds a Flask access log
    """
    log_level = get_log_level(app.config['TS_LOG_LEVEL'])
    ts_service = app.config['TS_SERVICE_NAME']
    ts_service = ts_service.replace('-', '_')

    # setup root logger
    logger = setup_root_logger(
        ts_service, log_level, FlaskRequestIDFilter()
    )

    # override flask logger
    del app.logger.handlers[:]
    app.logger.name = ts_service
    app.logger.setLevel(log_level)
    app.logger.addHandler(
        ts_stream_handler(FlaskRequestIDFilter())
    )

    @app.before_request
    def before_request():
        g.request_id = get_request_id()

    @app.after_request
    def after_request(response):
        level = logging.ERROR if response.status_code // 100 == 5 else logging.INFO
        extra = {
            'method': request.method, 'url': request.url, 'status': response.status_code
        }
        logger.log(
            level, '{method} {url} {status}'.format(**extra)
        )
        response.headers[TS_REQUEST_ID] = g.request_id

        return response


_register_id_getter(get_flask_request_id)
