import json
import pytest
from unittest.mock import patch

from faust import App as faust_app

from thunderstorm.kafka_messaging import (
    TSKafka, TSKafkaSendException, TSKafkaConnectException
)
from thunderstorm.shared import SchemaError


def test_TSKafka_init_raises_KeyError_for_missing_broker():
    # act
    with pytest.raises(KeyError) as exc:
        TSKafka('test-service')
    # assert
    assert "KeyError: 'broker'" in str(exc)


def test_TSKafka_init_sets_kafka_producer_to_None(tskafka):
    assert isinstance(tskafka, faust_app)
    assert tskafka.kafka_producer is None


def test_TSKafka_validate_data_returns_data(tskafka, TestEvent):
    # arrange
    data = {'int_1': 3, 'int_2': 6}
    # act
    validated_data = tskafka.validate_data(data, TestEvent)
    # assert
    assert json.loads(validated_data) == {'data': data}


def test_TSKafka_validate_data_raises_SchemaError(tskafka, TestEvent):
    # arrange
    data = {'int_1': 'a', 'int_2': 3}
    # act/assert
    with pytest.raises(SchemaError):
        tskafka.validate_data(data, TestEvent)


def test_TSKafka_send_ts_event_gets_kafka_producer_and_calls_send(tskafka, TestEvent):  # noqa
    # arrange
    class MockKafkaProducer():
        called = False

        def send(self, *args, **kwargs):
            self.called = True


    data = {'int_1': 3, 'int_2': 6}
    test_kafka_producer = MockKafkaProducer()

    # act
    with patch.object(
        tskafka, 'get_kafka_producer', return_value=test_kafka_producer
    ) as mock_get_kafka_producer:
        tskafka.send_ts_event(data, TestEvent)

    # assert
    mock_get_kafka_producer.assert_called_once()
    assert test_kafka_producer.called


def test_TSKafka_send_ts_event_if_send_raises_error_throw_TSKafkaSendException(
    tskafka, TestEvent, TestException
):
    # arrange
    class MockKafkaProducer():
        def send(self, *args, **kwargs):
            raise TestException()


    data = {'int_1': 3, 'int_2': 6}
    get_kafka_producer = patch.object(
        tskafka, 'get_kafka_producer', return_value=MockKafkaProducer()
    )

    # act
    with get_kafka_producer as mock_get_kafka_producer:
        with pytest.raises(TSKafkaSendException):
            tskafka.send_ts_event(data, TestEvent)

    # assert
    mock_get_kafka_producer.assert_called_once()


def test_TSKafka_get_kafka_producer_raises_TSKafkaConnectException_if_no_real_brokers(tskafka):  # noqa
    # act/assert
    with pytest.raises(TSKafkaConnectException):
        tskafka.get_kafka_producer()


@pytest.mark.asyncio
async def test_TSKafka_ts_event_calls_wrapped_function(tskafka, TestEvent):
    # arrange
    message = {'data': {'int_1': 3, 'int_2': 6}}

    # decorated agent
    @tskafka.ts_event(TestEvent)
    async def test_function(message):
        return message

    # act
    async with test_function.test_context() as agent:
        event = await agent.put(message.copy())

    # assert
    assert agent.results[event.message.offset] == message.pop('data')


@pytest.mark.asyncio
async def test_TSKafka_ts_event_increases_metric_count_and_raises_SchemaError(tskafka, TestEvent):
    # arrange
    class MockMonitor():
        class client():
            called = False

            def incr(self, arg):
                self.called = True

        client = client()


    message = {'data': {'int_1': 'not_an_int', 'int_2': 6}}
    tskafka.monitor = MockMonitor()

    # decorated agent
    @tskafka.ts_event(TestEvent)
    async def test_function(message):
        return message

    # act
    with pytest.raises(SchemaError):
        async with test_function.test_context() as agent:
            await agent.put(message.copy())

    assert tskafka.monitor.client.called
