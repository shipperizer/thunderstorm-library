from marshmallow import fields, Schema


class PaginationSchema(Schema):
    """
    Schema for describing the structure of the dict containing pagination info.
    """
    next_page = fields.String(required=False, dump_only=True)
    prev_page = fields.String(required=False, dump_only=True)
    total_records = fields.Integer(required=True, dump_only=True)
