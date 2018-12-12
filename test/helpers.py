from unittest import mock

from marshmallow import Schema, fields
import pytest


def patch_fixture(patch_path, scope='function', autouse=False, **kwargs):
    """Patch something as a pytest fixture."""

    def yield_patcher():
        with mock.patch(patch_path, **kwargs) as mocked_item:
            yield mocked_item

    return pytest.fixture(scope=scope, autouse=autouse)(yield_patcher)


class TestSchema(Schema):
    int_1 = fields.Integer()
    int_2 = fields.Integer()


class TestException(Exception):
    def __init__(self, message):
        self.message = message
