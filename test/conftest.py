from unittest.mock import MagicMock

import flask
from marshmallow import fields, Schema
import pytest

from thunderstorm.flask.headers import deprecated
from thunderstorm.flask.schemas import PaginationSchema


@pytest.fixture
def TestSchema():
    class TestSchema(Schema):
        int_1 = fields.Integer()
        int_2 = fields.Integer()

    return TestSchema


@pytest.fixture
def TestException():
    class TestException(Exception):
        def __init__(self, message):
            self.message = message

    return TestException


@pytest.fixture
def flask_app(mock_query):
    app = flask.Flask('test_app')

    @app.route('/past')
    @deprecated(deadline='2012-12-12')
    def past():
        return 'ok'

    @app.route('/future')
    @deprecated(deadline='2050-05-05')
    def future():
        return 'ok'

    @app.route('/none')
    @deprecated
    def none():
        return 'ok'

    return app


@pytest.fixture
def mock_query():
    query = MagicMock()
    query.count.return_value = 50

    def query_maker(num_items):
        return [
            {'int_1': 1, 'int_2': 2} for _ in range(num_items)
        ]

    query.offset.return_value.limit = query_maker

    return query


@pytest.fixture
def TestSchemaList(TestSchema):
    class TestSchemaList(PaginationSchema):
        data = fields.List(fields.Nested(TestSchema))

    return TestSchemaList
