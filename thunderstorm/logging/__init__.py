import uuid
import logging
""" You probably do not want to use this directly.
See:
    thunderstorm.logging.flask
    thunderstorm.logging.celery
"""

__all__ = [
    'gen_trace_id', 'get_request_id', 'ts_stream_handler', 'ts_logging_config', 'setup_root_logger'
]


_REQUEST_ID_GETTERS = []
TS_REQUEST_ID = 'TS-Request-ID'
TS_LOGGER_FORMAT_STR = '%(asctime)s %(levelname)s %(traceId)s %(process)d {}'.format(
    '%(thread)d %(pathname)s:%(lineno)d %(message)s'
)

LOGGING_LEVEL_MAPPER = {
    'INFO': logging.INFO, 'DEBUG': logging.DEBUG, 'NOTSET': logging.NOTSET,
    'CRITICAL': logging.CRITICAL, 'ERROR': logging.ERROR, 'WARNING': logging.WARNING
}


def get_log_level(level_str):
    if not level_str:
        raise ValueError('Invalid logging level')

    level_str = level_str.upper()
    if level_str not in LOGGING_LEVEL_MAPPER.keys():
        raise ValueError(f'The logging level {level_str} is not support')

    return LOGGING_LEVEL_MAPPER[level_str]


def _register_id_getter(getter):
    _REQUEST_ID_GETTERS.append(getter)


def gen_trace_id():
    """Return an unique trace id base on uuid4"""
    _trace_id = str(uuid.uuid4())

    return _trace_id.replace('-', '')


def get_request_id():
    """Return the current request ID

    Return the current request ID from whichever ID getters have been
    registered. An ID getter is registered when it's module is included.
    For example; if the ``thunderstorm.logging.flask`` module is imported
    the ``get_flask_request_id`` is registered.

    Returns:
        str the current request ID
    """
    for getter in _REQUEST_ID_GETTERS:
        request_id = getter()
        if request_id:
            return request_id

    return gen_trace_id()


def ts_stream_handler(ts_filter):
    """Create an stream handler"""
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter(TS_LOGGER_FORMAT_STR)
    )
    stream_handler.addFilter(ts_filter)

    return stream_handler


def ts_logging_config(ts_service, log_level):
    """Default logging config"""
    logging_config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': TS_LOGGER_FORMAT_STR
            },
        },
        'handlers': {
            'default': {
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                'level': log_level
            }
        },
        'loggers': {
            ts_service: {
                'propagate': True,
                'handlers': ['default'],
                'level': log_level
            }
        }
    }

    return logging_config


def setup_root_logger(ts_service, log_level, log_filter):
    """ used in flask & celery init, as we setup logger in faust and
    use the same logger, we don't need to call setup_root_logger in kafka init again"""
    logger = logging.getLogger(ts_service)
    logger.setLevel(log_level)
    logger.addHandler(
        ts_stream_handler(log_filter)
    )

    return logger
