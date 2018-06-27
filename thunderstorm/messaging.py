"""Thunderstorm messaging helpers"""
import collections

from celery.utils.log import get_task_logger
from celery.execute import send_task
from celery import shared_task
from statsd.defaults.env import statsd


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


def ts_task(event_name, schema):
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

    Returns:
        A decorator function
    """
    def decorator(task_func):
        task_name = ts_task_name(event_name)

        def task_handler(message):
            ts_message = TSMessage(message.pop('data'), message)

            deserialized_data, errors = schema.load(ts_message)
            if errors:
                statsd.incr('tasks.{}.ts_task.errors.schema'.format(task_name))
                error_msg = 'inbound schema validation error for event {}'.format(event_name)  # noqa
                logger.error(
                    error_msg,
                    extra={'errors': errors, 'data': ts_message}
                )
                raise SchemaError(error_msg, errors=errors, data=ts_message)
            else:
                logger.info('received ts_task on {}'.format(event_name))
                ts_message.data = deserialized_data
                return task_func(ts_message)

        return shared_task(name=task_name)(task_handler)

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
        data (dict or list): The event data to be emitted

    Raises:
        SchemaError if schema validation fails.

    Returns:
        The result of the send_task call.
    """

    if {'name', 'args', 'exhange', 'routing_key'} & set(kwargs.keys()):
        raise ValueError('Cannot override name, args, exchange or routing_key')
    task_name = ts_task_name(event_name)
    errors = schema.load(data).errors
    if errors:
        statsd.incr('tasks.{}.send_ts_task.errors.schema'.format(task_name))
        error_msg = 'outbound schema validation error for event {}'.format(event_name)  # noqa
        logger.error(error_msg, extra={'errors': errors, 'data': data})

        raise SchemaError(error_msg, errors=errors, data=data)
    else:
        logger.info('send_ts_task on {}'.format(event_name))
        event = {
            'data': data
        }
        return send_task(
            task_name,
            (event,),
            exchange='ts.messaging',
            routing_key=event_name,
            **kwargs
        )
