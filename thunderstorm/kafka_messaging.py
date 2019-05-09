import collections
import logging

from kafka import KafkaProducer
from marshmallow import Schema, fields
from marshmallow.exceptions import ValidationError

from thunderstorm.shared import SchemaError, ts_task_name


import marshmallow  # TODO: @will-norris backwards compat - remove
MARSHMALLOW_2 = int(marshmallow.__version__[0]) < 3


def init_ts_kafka(faust_app):
    def ts_event(topic, schema, *args, **kwargs):
        """Decorator for Thunderstorm messaging events

        Example:
            @ts_event('domain.action.request', DomainActionRequestSchema())
            async def handle_domain_action_request(message):
                # do something with validated message

        Args:
            topic (str): The topic name
            schema (marshmallow.Schema): The schema instance expected by this task

        Returns:
            A decorator function
        """
        def decorator(func):
            async def event_handler(*args):

                """
                args can contain up to 1 item, which is the message

                @ts_event
                async def handle_message(message):
                    return message

                """
                if len(args) == 1:
                    return await _event_handler(args[0])
                else:
                    raise NotImplementedError('Maximum 1 parameter allowed for ts_task_v2 decorator')

            async def _event_handler(stream):
                # stream handling done in here, no need to do it inside the func
                async for message in stream:
                    ts_message = message.pop('data') or message

                    try:
                        deserialized_data = schema.load(ts_message)
                    except ValidationError as vex:
                        faust_app.monitor.client.incr(f'event.{topic}.errors.schema')
                        error_msg = f'inbound schema validation error for event {topic}'
                        logging.error(error_msg, extra={'errors': vex.messages, 'data': ts_message})
                        raise SchemaError(error_msg, errors=vex.messages, data=ts_message)
                    else:
                        logging.debug(f'received ts_event on {topic}')
                        await func(deserialized_data)

            return faust_app.agent(topic, name=f'thunderstorm.messaging.{ts_task_name(topic)}')(event_handler)

        return decorator

    # create ts_event decorator on faust app
    faust_app.ts_event = ts_event


class TSKafkaSendException(Exception):
    pass


class TSKafkaConnectException(Exception):
    pass


# Keep topic names and schemas together
Event = collections.namedtuple('Event', ['schema', 'topic'])


class TSKafkaProducer:
    def __init__(self, brokers):
        """
        Create a new TSKafkaProducer

        Args:
            brokers (list or string): ['kafka:9092'] or 'kafka1:9092,kafka2:9092'
        """
        self.brokers = brokers

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
            data = schema.dumps(data).data
            errors = schema.loads(data).errors

            if errors:
                error_msg = f'Outbound schema validation error for event {event.topic}'  # noqa
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
                error_msg = f'Outbound schema validation error for event {event.topic}'  # noqa
                logging.error(error_msg, extra={'errors': vex.messages, 'data': data})
                raise SchemaError(error_msg, errors=vex.messages, data=data)

        return data.encode('utf-8')

    def send_ts_event(self, data, event):
        """
        Send a message to a kafka broker

        Args:
            event (namedtuple): Has attributes schema and topic
            data (dict): Message you want to send via the message bus
        """
        serialized = self.validate_data(data, event)
        producer = self.get_kafka_producer()
        try:
            producer.send(event.topic, value=serialized)  # send takes raw bytes
            producer.flush()  # flush any pending messages
        except Exception as ex:
            raise TSKafkaSendException(f'Exception while pushing message to broker: {ex}')
        finally:
            producer.close()  # how long lived do we want connections to be?

    def get_kafka_producer(self):
        try:
            return KafkaProducer(bootstrap_servers=self.brokers)
        except Exception as ex:
            raise TSKafkaConnectException(f'Exception while connecting to Kafka: {ex}')
