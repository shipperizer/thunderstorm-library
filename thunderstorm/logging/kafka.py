import logging
from faust import current_event
from . import _register_id_getter, get_request_id

__all__ = ['KafkaRequestIDFilter']


class KafkaRequestIDFilter(logging.Filter):
    def filter(self, record):
        record.traceId = get_request_id()

        return record


def get_kafka_request_id():
    event = current_event()
    if event and event.message:
        return event.value.get('trace_id', None)

    return None


_register_id_getter(get_kafka_request_id)
