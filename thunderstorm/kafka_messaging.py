import collections
import logging

import faust
from kafka import KafkaProducer
from marshmallow import Schema, fields
from marshmallow.exceptions import ValidationError

from thunderstorm.shared import SchemaError, ts_task_name


import marshmallow  # TODO: @will-norris backwards compat - remove
MARSHMALLOW_2 = int(marshmallow.__version__[0]) < 3

# Keep topic names and schemas together
Event = collections.namedtuple('Event', ['topic', 'schema'])


class TSKafkaSendException(Exception):
    pass


class TSKafkaConnectException(Exception):
    pass


class TSKafka(faust.App):
    """
    Wrapper class for combining features of faust and Kafka-Python. The broker
    argument can be passed as a string of the form 'kafka-1:9092,kafka-2:9092'
    and the construcor will format the string as required by faust.
    """

    def __init__(self, *args, **kwargs):
        self.broker = kwargs['broker']
        self.kafka_producer = None
        kwargs['broker'] = ';'.join([f'kafka://{broker}' for broker in kwargs['broker'].split(',')])
        super().__init__(*args, **kwargs)

    def validate_data(self, data, event):
        """
        Validate message data by dumping to a string and loading it back

        Args:
            data (dict): Message to be serialized
            event (namedtuple): Contains topic and schema

        Returns:
            bytes: Serialized message

        Raises:
            SchemaError: If message validation fails for any reason
        """
        class TSMessageSchema(Schema):
            data = fields.Nested(event.schema)

        schema = TSMessageSchema()

        # Marshmallow 2 compatibility - remove when no longer needed
        if MARSHMALLOW_2:
            serialized_data, errors = schema.dumps({'data': data})

            if errors:
                error_msg = 'Error serializing queue message data.'
                logging.error(error_msg, extra={'errors': errors, 'data': data})
                raise SchemaError(error_msg, errors=errors, data=data)
            else:
                data = serialized_data

            errors = schema.loads(data).errors

            if errors:
                error_msg = f'Outbound schema validation error for event {event.topic}'
                logging.error(error_msg, extra={'errors': errors, 'data': data})
                raise SchemaError(error_msg, errors=errors, data=data)
        else:
            try:
                data = schema.dumps({'data': data})
            except ValidationError as vex:
                error_msg = 'Error serializing queue message data'
                logging.error(error_msg, extra={'errors': vex.messages, 'data': data})
                raise SchemaError(error_msg, errors=vex.messages, data=data)

            try:
                schema.loads(data)
            except ValidationError as vex:
                error_msg = f'Outbound schema validation error for event {event.topic}'
                logging.error(error_msg, extra={'errors': vex.messages, 'data': data})
                raise SchemaError(error_msg, errors=vex.messages, data=data)

        return data.encode('utf-8')

    def send_ts_event(self, data, event, key=None):
        """
        Send a message to a kafka broker. We only connect to kafka when first
        sending a message.

        Args:
            event (namedtuple): Has attributes schema and topic
            data (dict): Message you want to send via the message bus
            key (str): Key to use when routing messages to a partition - It is
            recommended you use the resource identifier so all messages relating
            to a particular resource get routed to the same partition. A value of
            None will cause messages to randomly sent to different partitions
        """
        serialized = self.validate_data(data, event)

        if not self.kafka_producer:
            self.kafka_producer = self.get_kafka_producer()

        try:
            self.kafka_producer.send(event.topic, value=serialized, key=key)  # send takes raw bytes
        except Exception as ex:
            raise TSKafkaSendException(f'Exception while pushing message to broker: {ex}')

    def get_kafka_producer(self):
        """
        Return a KafkaProducer instance with sensible defaults
        """
        try:
            return KafkaProducer(
                bootstrap_servers=self.broker,
                connections_max_idle_ms=60000,
                max_in_flight_requests_per_connection=25,
                key_serializer=lambda x: x.encode()
            )
        except Exception as ex:
            raise TSKafkaConnectException(f'Exception while connecting to Kafka: {ex}')

    def ts_event(self, event, *args, **kwargs):
        """Decorator for Thunderstorm messaging events

        Examples:
            @ts_event(Event('domain.action.request', DomainActionRequestSchema))
            async def handle_domain_action_request(message):
                # do something with validated message

        Args:
            topic (str): The topic name
            schema (marshmallow.Schema): The schema class expected by this task

        Returns:
            A decorator function
        """
        topic = event.topic
        schema = event.schema()

        def decorator(func):
            async def event_handler(stream):
                # stream handling done in here, no need to do it inside the func
                async for message in stream:
                    ts_message = message.pop('data') or message

                    # Marshmallow 2 compatibility - remove when no longer needed
                    if MARSHMALLOW_2:
                        deserialized_data, errors = schema.load(ts_message)
                        if errors:
                            self.monitor.client.incr(f'event.{topic}.errors.schema')
                            error_msg = f'Inbound schema validation error for event {event.topic}'
                            logging.error(error_msg, extra={'errors': errors, 'data': ts_message})
                            raise SchemaError(error_msg, errors=errors, data=ts_message)
                    else:
                        try:
                            deserialized_data = schema.load(ts_message)
                        except ValidationError as vex:
                            self.monitor.client.incr(f'event.{topic}.errors.schema')
                            error_msg = f'Inbound schema validation error for event {topic}'
                            logging.error(error_msg, extra={'errors': vex.messages, 'data': ts_message})
                            raise SchemaError(error_msg, errors=vex.messages, data=ts_message)

                    logging.debug(f'received ts_event on {topic}')
                    yield await func(deserialized_data)

            return self.agent(topic, name=f'thunderstorm.messaging.{ts_task_name(topic)}')(event_handler)

        return decorator
