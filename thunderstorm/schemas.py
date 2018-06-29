from marshmallow import Schema, fields


class PaginationSchema(Schema):
    """
    Schema for describing the structure of the dict containing pagination info.
    """
    next_page = fields.String(required=False, dump_only=True, description='Next page uri')
    prev_page = fields.String(required=False, dump_only=True, description='Previous page uri')
    total_records = fields.Integer(required=False, dump_only=True, description='Total number of entries')


class HttpErrorResponseSchema(Schema):
    """
    Schema for standard HTTP errors (4XX,5XX)
    """
    message = fields.String(description='Description of the error happened during the response')
    code = fields.Integer(description='HTTP code of the response')
