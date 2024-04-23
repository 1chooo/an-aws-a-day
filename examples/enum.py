from enum import Enum
class Status(Enum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    FORBIDDEN = 403
    INTERNAL_SERVER_ERROR = 500

    def get_value(self):
        return self.value