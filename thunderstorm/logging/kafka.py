import logging

__all__ = ['KafkaRequestIDFilter']

from . import get_request_id


class KafkaRequestIDFilter(logging.Filter):
    def filter(self, record):
        record.traceId = get_request_id()

        return record
