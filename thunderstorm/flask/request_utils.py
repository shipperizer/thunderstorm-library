from urllib.parse import urlparse

from flask import request

from thunderstorm.flask.exceptions import DeserializationError
from thunderstorm.flask.schemas import PaginationRequestSchema


def make_paginated_response(query, url_path, schema, page, page_size):
    """
    Take a sqlalchemy query and paginate it based on the args provided.

    Args:
        query (sqlalchemy Query object): Query you wish to paginate
        url_path (str): url_path that the request was sent to e.g. for the url
            'http://localhost/foo/bar/baz/' it would be '/foo/bar/baz'.
            Query parameters are stripped out by the get_pagination_info func
        schema (Schema): Subclass of marshmallow.Schema
        page (int): Page number of the results page to return
        page_size (int): Number of results to return per page

    Returns:
        dict: The structure of which conforms to the thunderstorm API
            spec response structure
    """
    start = (page - 1) * page_size
    num_records = query.count()

    response = get_pagination_info(page, page_size, num_records, url_path)
    query = query.offset(start).limit(page_size)

    # python34 does not support **pagination_info when creating a dict so update the repsonse dict manually
    response['data'] = query
    return schema().dump(response).data


def get_request_pagination(params=None, exc=DeserializationError):
    """
    Get pagination params from a dict. Modifies the dict passed to it.
    If no params are provided it falls back to using flask's request.args

    Args:
        params (dict): Dictionary that must contain page and page_size keys
        exc (Exception subclass): Custom exception to raise if validation of
            query params fails, falls back to DeserializationError if none is provided

    Raises:
        KeyError: If either page or page_size are missing
        exc or DeserializationError: If there are any marshmallow validation errors
    """
    if params:
        return {'page': params.pop('page'), 'page_size': params.pop('page_size')}

    params = request.args

    pagination, errors = PaginationRequestSchema().load(params)
    if errors:
        raise exc('Error deserializing pagination options: {}'.format(errors))

    return pagination


def get_request_filters(schema, exc):
    """Get all query params from from a flask request object, deserialize them and
       raise an exception if there are any errors and a custom exception is provided

    Args:
        schema (marshmallow.Schema): Subclass of marshmallow.schema
        exc (Exception): Exception subclass to raise if there are deserialization errors

    Raises:
        exc: If there are any marshmallow validation errors deserializing request.args
    """
    data, errors = schema().load(request.args)
    if errors:
        raise exc('Error deserializing filters provided: {}'.format(errors))

    return data


def _strip_query(url_path):
    """
    Strip out query params page and page_size from the query params

    Args:
        url_path (str): Path of the URL the request was made to

    Returns:
        str: query params string without page and page_size
    """
    query = urlparse(url_path).query

    if query:
        # remove page and page_size
        query = [
            params for params in query.split('&')
            if not params.startswith(('page', 'page_size'))
        ]
        # rejoin query params
        query = '&'.join(query)

    return query


def get_pagination_info(page, page_size, num_records, url_path):
    """
    Utility function for creating a dict of pagination information.

    Args:
        page (int): Requested page number of results
        page_size (int): Number of results to display per page
        num_records (int): Total number of records in the db for the given query
        url_path (str): Path of the URL the request was made to

    Returns:
        dict: Dict containining pagination information. The structure of this
            dict should match the PaginationSchema in schemas.py
    """
    # get query args if exist strip out page_size and page query args
    query = _strip_query(url_path)

    # strip url to be just the path
    url_path = urlparse(url_path).path

    next_page = page + 1 if page < num_records / page_size else None
    prev_page = page - 1 if page != 1 else None

    pagination_info = {}

    if query:
        base_url = '{}?{}&page_size={}'.format(url_path, query, page_size)
    else:
        base_url = '{}?page_size={}'.format(url_path, page_size)

    if next_page:
        pagination_info['next_page'] = '{}&page={}'.format(base_url, next_page)
    if prev_page:
        pagination_info['prev_page'] = '{}&page={}'.format(base_url, prev_page)

    pagination_info['total_records'] = num_records
    return pagination_info


# TODO: @will-norris Deprecate in favour of make_paginated_response
def paginate(query, page, page_size, url_path):
    """
    Take a sqlalchemy query and paginate it based on the args provided.

    Args:
        query (sqlalchemy Query object): Query you wish to paginate
        page (int): Page number of the results page to return
        page_size (int): Number of results to return per page
        url_path (str): url_path that the request was sent to e.g. for the url
            'http://localhost/foo/bar/baz/' it would be '/foo/bar/baz'.
            Query parameters are stripped out by the get_pagination_info func.

    Returns:
        tuple: (Paginated Query object applied to it, dict of pagination info)
    """
    start = (page - 1) * page_size
    num_records = query.count()

    pagination_info = get_pagination_info(page, page_size, num_records, url_path)

    return query.offset(start).limit(page_size), pagination_info
