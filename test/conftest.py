import flask
from marshmallow import fields, Schema
import pytest

from thunderstorm.flask.headers import deprecated


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
def flask_app():
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
