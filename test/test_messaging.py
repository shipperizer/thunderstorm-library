from unittest.mock import patch, Mock
from uuid import uuid4

from marshmallow import Schema, fields
import pytest

from thunderstorm.messaging import (
    ts_task_name, ts_task, send_ts_task, SchemaError
)


@pytest.mark.parametrize('event_name,task_name', [
    ('foo.bar', 'handle_foo_bar'),
    ('foo.bar-and.other', 'handle_foo_bar_and_other'),
    ('foo', 'handle_foo'),
    ('foo.bar.v2', 'handle_foo_bar_v2'),
    ('foo.bar.v2-beta1', 'handle_foo_bar_v2_beta1'),
    ('', 'handle_')
])
def test_ts_task_name(event_name, task_name):
    assert ts_task_name(event_name) == task_name


class FooSchema(Schema):
    foo = fields.String(required=True)
    bar = fields.String(required=False)
    baz = fields.UUID(required=False)


@patch('thunderstorm.messaging.shared_task')
def test_ts_task_calls_shared_task(mock_shared_task):
    # act
    @ts_task('foo.bar', schema=FooSchema)
    def my_task(message):
        # since shared_task is patched the body of this task is never called
        pass

    # act
    my_task({'data': {'foo': 'bar'}, 'request_id': 123})

    # assert
    mock_shared_task.assert_called_once_with(
        name='handle_foo_bar'
    )


def test_ts_task_deserializes_data():
    # arrange
    some_uuid = uuid4()

    # act
    @ts_task('foo.bar', schema=FooSchema())
    def my_task(message):
        assert message == {'foo': 'bar', 'baz': some_uuid}
        assert message.metadata == {'request_id': 123}
        assert message.data == {'foo': 'bar', 'baz': some_uuid}

    # act
    my_task({'data': {'foo': 'bar', 'baz': str(some_uuid)}, 'request_id': 123})


def test_ts_task_fails_on_schema_error():
    mock_task = Mock()
    my_task = ts_task('foo.bar', schema=FooSchema())(mock_task)

    with pytest.raises(SchemaError):
        my_task({'data': {'bar': 'foo'}, 'request_id': 123})


def test_send_ts_task_with_one(celery):
    # act
    with patch.object(celery, 'send_task') as mock_send_task:
        send_ts_task('foo.bar', FooSchema(), {'foo': 'bar'})

    # assert
    mock_send_task.assert_called_once_with(
        'handle_foo_bar', ({'data': {'foo': 'bar'}},),
        exchange='ts.messaging',
        routing_key='foo.bar'
    )


def test_send_ts_task_with_many(celery):
    # act
    with patch.object(celery, 'send_task') as mock_send_task:
        send_ts_task('foo.bar', FooSchema(many=True), [{'foo': 'bar'}])

    # assert
    mock_send_task.assert_called_once_with(
        'handle_foo_bar', ({'data': [{'foo': 'bar'}]},),
        exchange='ts.messaging',
        routing_key='foo.bar'
    )


def test_send_ts_task_raises_SchemaError_on_schema_validation_deserilization(celery):
    # assert
    with pytest.raises(SchemaError):
        # act
        with patch.object(celery, 'send_task') as mock_send_task:
            send_ts_task('foo.bar', FooSchema(many=False), {'baz': 'foo'})

    # assert
    assert not mock_send_task.called


def test_send_ts_task_raises_SchemaError_on_schema_validation_serilization(celery):
    # assert
    with pytest.raises(SchemaError):
        # act
        with patch.object(celery, 'send_task') as mock_send_task:
            send_ts_task('foo.bar', FooSchema(many=False), {'baz': 'not_a_uuid'})

    # assert
    assert not mock_send_task.called


def test_send_ts_task_fails_on_one_when_expecting_many(celery):
    # assert
    with pytest.raises(SchemaError):
        # act
        with patch.object(celery, 'send_task') as mock_send_task:
            send_ts_task('foo.bar', FooSchema(many=True), {'foo': 'bar'})

    # assert
    assert not mock_send_task.called


def test_send_ts_task_fails_on_many_when_expecting_one(celery):
    # assert
    with pytest.raises(SchemaError):
        # act
        with patch.object(celery, 'send_task') as mock_send_task:
            send_ts_task('foo.bar', FooSchema(many=False), [{'foo': 'bar'}])

    # assert
    assert not mock_send_task.called
