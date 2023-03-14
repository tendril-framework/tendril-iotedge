

from tendril.common.exceptions import HTTPCodedException


class DeviceTypeUnrecognized(HTTPCodedException):
    status_code = 406

    def __init__(self, appname, id=None):
        self.appname = appname
        self.id = id

    def __str__(self):
        if not self.id:
            return f"Device type '{self.appname}' is unrecognized."
        return f"Device type provided by '{self.id}', '{self.appname}' is unrecognized."


class DeviceTypeMismatch(HTTPCodedException):
    status_code = 409

    def __init__(self, actual, expected, id=None):
        self.actual = actual
        self.expected = expected
        self.id = id

    def __str__(self):
        if not self.id:
            return f"Device type mismatch. Got '{self.actual}', expecting '{self.expected}'"
        return f"Device type of '{self.id}' ('{self.actual}') " \
               f"does not match the required or registered type " \
               f"'{self.expected}'"
