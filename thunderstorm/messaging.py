"""Thunderstorm messaging helpers"""
import collections
import logging

from celery.utils.log import get_task_logger
from celery import current_app, shared_task
from marshmallow.exceptions import ValidationError
from statsd.defaults.env import statsd


import marshmallow  # TODO: @will-norris backwards compat - remove
MARSHMALLOW_2 = int(marshmallow.__version__[0]) < 3

logger = get_task_logger(__name__)


def ts_task_name(event_name):
    """Return the task name derived from the event name

    This function implements the rules described in the Thunderstorm messaging
    spec.

    Args:
        event_name (str): The event name (this is also the routing key)

    Returns:
        task_name (str)
    """
    task_name = event_name
    for c in '.-':
        task_name = task_name.replace(c, '_')

    return 'handle_{}'.format(task_name)


class TSMessage(collections.abc.Mapping):
    def __init__(self, data, metadata):
        self.data = data
        self.metadata = metadata

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)


def ts_task(event_name, schema, bind=False, **options):
    """Decorator for Thunderstorm messaging tasks

    The task name is derived from the event name.

    See: ts_task_name

    Example:
        @ts_task('domain.action.request', schema=DomainActionRequestSchema())
        def handle_domain_action_request(message):
            # do something with validated message

    Args:
        event_name (str): The event name (this is also the routing key)
        schema (marshmallow.Schema): The schema instance expected by this task
        bind (bool): if the task is bound
        options (dict): extra options to be passed to the shared_task decorator

    Returns:
        A decorator function
    """
    def decorator(task_func):
        task_name = ts_task_name(event_name)

        def task_handler(*args):
            """
            args can contain up to 2 items:
            * if a bound task the first arg will be self and the second will be message
            * if an unbound task, only one arg will be present and that will be the message

            @ts_task(bind=True)
            def task_a(self, message):
                return message

            @ts_task
            def task_b(message):
                return message
            """
            # if only one argument then it's not a bound task, if two then it is
            # more than 2 args are not allowed
            if len(args) == 1:
                return _task_handler(message=args[0])
            elif len(args) == 2:
                return _task_handler(self=args[0], message=args[1])
            else:
                raise NotImplementedError('Maximum 2 parameters allowed for ts_task decorator')

        def _task_handler(self=None, message=None):
            ts_message = TSMessage(message.pop('data'), message)

            # TODO: @will-norris backwards compat - remove
            if MARSHMALLOW_2:
                deserialized_data, errors = schema.load(ts_message)
                if errors:
                    statsd.incr('tasks.{}.ts_task.errors.schema'.format(task_name))
                    error_msg = 'inbound schema validation error for event {}'.format(event_name)
                    logger.error(error_msg, extra={'errors': errors, 'data': ts_message})
                    raise SchemaError(error_msg, errors=errors, data=ts_message)
                else:
                    logger.info('received ts_task on {}'.format(event_name))
                    ts_message.data = deserialized_data
                    # passing task_func instead of passing self - @will-norris
                    return task_func(self, ts_message) if bind else task_func(ts_message)
            else:
                try:
                    deserialized_data = schema.load(ts_message)
                except ValidationError as vex:
                    statsd.incr('tasks.{}.ts_task.errors.schema'.format(task_name))
                    error_msg = 'inbound schema validation error for event {}'.format(event_name)
                    logger.error(error_msg, extra={'errors': vex.messages, 'data': ts_message})
                    raise SchemaError(error_msg, errors=vex.messages, data=ts_message)
                else:
                    logger.info('received ts_task on {}'.format(event_name))
                    ts_message.data = deserialized_data
                    # passing task_func instead of passing self - @will-norris
                    return task_func(self, ts_message) if bind else task_func(ts_message)

        return shared_task(bind=bind, name=task_name, **options)(task_handler)

    return decorator


class SchemaError(Exception):
    def __init__(self, message, *, errors=None, data=None):
        super().__init__(message)
        self.errors = errors
        self.data = data

    def __str__(self):
        return '{}: {} with {}'.format(super().__str__(), self.errors, self.data)


def send_ts_task(event_name, schema, data, **kwargs):
    """Send a Thunderstorm messaging event

    The correct task name is derived from the event name.

    Example:
        send_ts_task(
            'domain.action.request', DomainActionRequestSchema(),
            payload
        )

    Args:
        event_name (str): The event name (this is also the routing key)
        schema (marshmallow.Schema): The schema instance the payload must
                                     comply to
        data (dict or list): The event data to be emitted (does not need to be serialized yet)

    Raises:
        SchemaError If schema validation fails.

    Returns:
        The result of the send_task call.
    """

    if {'name', 'args', 'exchange', 'routing_key'} & set(kwargs.keys()):
        raise ValueError('Cannot override name, args, exchange or routing_key')
    task_name = ts_task_name(event_name)

    # TODO: @will-norris backwards compat - remove
    if MARSHMALLOW_2:
        data = schema.dump(data).data

        data, errors = schema.load(data)
        if errors:
            statsd.incr('tasks.{}.send_ts_task.errors.schema'.format(task_name))
            error_msg = 'Outbound schema validation error for event {}'.format(event_name)  # noqa
            logger.error(error_msg, extra={'errors': errors, 'data': data})

            raise SchemaError(error_msg, errors=errors, data=data)
        else:
            logger.info('send_ts_task on {}'.format(event_name))
            event = {
                'data': data
            }
            return current_app.send_task(
                task_name,
                (event,),
                exchange='ts.messaging',
                routing_key=event_name,
                **kwargs
            )
    else:
        try:
            data = schema.dump(data)
        except ValidationError as vex:
            error_msg = 'Error serializing queue message data'
            raise SchemaError(error_msg, errors=vex.messages, data=data)

        try:
            schema.load(data)
        except ValidationError as vex:
            statsd.incr('tasks.{}.send_ts_task.errors.schema'.format(task_name))
            error_msg = 'Outbound schema validation error for event {}'.format(event_name)  # noqa
            logger.error(error_msg, extra={'errors': vex.messages, 'data': data})

            raise SchemaError(error_msg, errors=vex.messages, data=data)
        else:
            logger.info('send_ts_task on {}'.format(event_name))
            event = {
                'data': data
            }
            return current_app.send_task(
                task_name,
                (event,),
                exchange='ts.messaging',
                routing_key=event_name,
                **kwargs
            )


# ################################## KAFKA ############################### #

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
        _topic = faust_app.topic(topic, value_type=bytes)


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
                        statsd.incr('tasks.{}.ts_event.errors.schema'.format(topic))
                        error_msg = 'inbound schema validation error for event {}'.format(topic)
                        logging.error(error_msg, extra={'errors': vex.messages, 'data': ts_message})
                        raise SchemaError(error_msg, errors=vex.messages, data=ts_message)
                    else:
                        logging.info('received ts_event on {}'.format(topic))
                        await func(deserialized_data)

            return faust_app.agent(_topic, name=f'thunderstorm.messaging.{ts_task_name(topic)}')(event_handler)

        return decorator

    # create ts_event decorator on faust app
    faust_app.ts_event = ts_event
