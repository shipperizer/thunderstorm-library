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


class SchemaError(Exception):
    def __init__(self, message, *, errors=None, data=None):
        super().__init__(message)
        self.errors = errors
        self.data = data

    def __str__(self):
        return '{}: {} with {}'.format(super().__str__(), self.errors, self.data)
