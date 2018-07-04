from urllib.parse import urlparse


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
    # strip url to be just the path
    url_path = urlparse(url_path).path

    next_page = page + 1 if page < num_records / page_size else None
    prev_page = page - 1 if page != 1 else None

    pagination_info = {}
    base_url = '{}?page_size={}'.format(url_path, page_size)

    if next_page:
        pagination_info['next_page'] = '{}&page={}'.format(base_url, next_page)
    if prev_page:
        pagination_info['prev_page'] = '{}&page={}'.format(base_url, prev_page)

    pagination_info['total_records'] = num_records
    return pagination_info


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
