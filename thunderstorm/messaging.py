"""Thunderstorm messaging helpers"""
import collections

from celery.utils.log import get_task_logger
from celery import current_app, shared_task
from marshmallow.exceptions import ValidationError
from statsd.defaults.env import statsd

from thunderstorm.shared import SchemaError, ts_task_name


import marshmallow  # TODO: @will-norris backwards compat - remove
MARSHMALLOW_2 = int(marshmallow.__version__[0]) < 3

logger = get_task_logger(__name__)


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
