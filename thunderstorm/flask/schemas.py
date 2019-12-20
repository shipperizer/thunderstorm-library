from marshmallow import Schema, fields
from marshmallow.validate import Range

from thunderstorm.flask.headers import rewrite_path


class PaginationSchema(Schema):
    """
    Schema for describing the structure of the dict containing pagination info.
    """
    next_page = fields.Function(
        lambda obj: rewrite_path(obj['next_page']) if obj.get('next_page') else None,
        required=False, dump_only=True, default=None, description='Next page uri'
    )
    prev_page = fields.Function(
        lambda obj: rewrite_path(obj['prev_page']) if obj.get('prev_page') else None,
        required=False, dump_only=True, default=None, description='Previous page uri'
    )
    total_records = fields.Integer(required=False, dump_only=True, description='Total number of entries')


class PaginationRequestSchema(Schema):
    """
    Validate pagination params on listing endpoints.
    """
    page = fields.Integer(
        validate=Range(min=1), missing=1, description='Page number, minimum value is 1, defaults to 1.'
    )
    page_size = fields.Integer(
        validate=Range(min=1, max=100),
        missing=20,
        description='Number of resources per page to display in the result. Defaults to 20'
    )


class HttpErrorResponseSchema(Schema):
    """
    Schema for standard HTTP errors (4XX,5XX)
    """
    message = fields.String(
        description='Description of the error happened during the response')
    code = fields.Integer(description='HTTP code of the response')


class PaginationRequestSchemaV2(Schema):
    """
    Validate pagination params on listing endpoints. version 2
    """
    page_num = fields.Integer(
        validate=Range(min=1), missing=1, description='Page number, minimum value is 1, defaults to 1.'
    )
    page_size = fields.Integer(
        validate=Range(min=1, max=1000),
        missing=20,
        description='Number of resources per page to display in the result. Defaults to 20'
    )


class PaginationSchemaV2(PaginationRequestSchemaV2):
    """
    Schema for describing the structure of the dict containing pagination info. Version 2
    """
    items = fields.Integer(required=True, dump_only=True, description='Total number of entries')
    total_page = fields.Integer(required=True, dump_only=True, description='Total number of pages')
