import datetime
import functools
import logging
from urllib.parse import urlparse

from dateutil import parser
from flask import request, make_response


logger = logging.getLogger(__name__)


def deprecated(route=None, *, deadline=None):
    """Mark a Flask route deprecated

    Log a warning on access to the route and add a Warning HTTP header
    informing the client.

    After the deadline has been reached continue to serve the route but
    start logging as error.

    Warning header as per RFC7234
    https://tools.ietf.org/html/rfc7234#section-5.5

    Example:
        @app.route('/foo/bar')
        @deprecated(deadline='2018-08-10')
        def my_route():

    Args:
        route (callable): Flask route to decorate
        deadline (datetime or str): when this route will be disabled
    """
    if deadline is not None and not isinstance(deadline, datetime.datetime):
        deadline = parser.parse(deadline)

    def decorator(route):
        @functools.wraps(route)
        def decorated_route(*args, **kwargs):
            message = 'Call to deprecated route: {}'.format(request.path)
            if deadline and deadline < datetime.datetime.utcnow():
                logger.error(message)
            else:
                logger.warning(message)

            resp = make_response(route(*args, **kwargs))

            resp.headers['Warning'] = warning_header(deadline=deadline)

            return resp

        return decorated_route

    if callable(route):
        return decorator(route)
    elif route is None:
        return decorator
    else:
        raise TypeError('Non-callable supplied to decorator')


def warning_header(deadline):
    message = 'Deprecated route'
    if deadline:
        message = '{}, will be maintained until {}'.format(message, deadline.isoformat())

    return '299 - "{}"'.format(message)


def rewrite_path(path):
    """Rewrite a path based on API gateway's rewriting

    """
    if 'TS-Rewritten' in request.headers:
        return rewrite_path_with_header(path, request.headers['TS-Rewritten'])

    return path


def rewrite_path_with_header(path, header):
    """Rewrite a path based on API gateway's rewriting

    Takes a header in the form
    'type=<type>; source=<origin_path>; target=<target_path>'
    and a path and returns the path rewritten for the other side of the proxy.
    """
    try:
        rewritten = _parse_rewritten_header(header)
        if rewritten['type'] == 'transparent':
            return path
        elif rewritten['type'] == 'static':
            query = urlparse(path).query
            if query:
                return '{}?{}'.format(rewritten['source'], query)
            return rewritten['source']
        elif rewritten['type'] == 'prefix':
            # TODO @robyoung fix this quick hack
            source, target = _chop_common_suffix(
                rewritten['source'], rewritten['target']
            )
            if path.startswith(target):
                return source + path[len(target):]
            else:
                raise ValueError
        else:
            raise ValueError
    except Exception:
        logger.warning('Invalid TS-Rewritten header "{}"'.format(header))
        return path


def _parse_rewritten_header(header):
    pairs = [part.strip().split('=') for part in header.split(';')]
    if any(len(pair) != 2 for pair in pairs):
        raise ValueError
    return dict(pairs)


def _chop_common_suffix(source, target):
    """Chop common suffix of both paths

    >>> _chop_common_suffix('/api/v1/suffix', '/api/v2/suffix')
    ('/api/v1', '/api/v2')
    """
    source_parts = source.split('/')
    target_parts = target.split('/')

    i = -1
    while source_parts[i] == target_parts[i]:
        i -= 1
    i += 1

    if i < 0:
        return ('/'.join(source_parts[:i]), '/'.join(target_parts[:i]))
    else:
        return (source, target)
