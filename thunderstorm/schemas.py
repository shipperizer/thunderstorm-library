from marshmallow import Schema, fields

from thunderstorm.flask import rewrite_path


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


class HttpErrorResponseSchema(Schema):
    """
    Schema for standard HTTP errors (4XX,5XX)
    """
    message = fields.String(
        description='Description of the error happened during the response')
    code = fields.Integer(description='HTTP code of the response')
