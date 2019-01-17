class DeserializationError(Exception):
    def __init__(self, message):
        self.message = message


class SerializationError(Exception):
    def __init__(self, message):
        self.message = message
