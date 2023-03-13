

from functools import wraps

from .registration import registered_device

from tendril.utils.db import with_db
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


def mark_seen(func):
    @wraps(func)
    def inner(device=None, session=None, **kwargs):
        logger.info(f"Mark device {device} as seen")
        func(*args, device=device, session=session, **kwargs)
    return inner


@with_db
@registered_device()
@mark_seen
def ping(device=None, status=None, session=None):
    pass


def announce_device(device_id, appname, session=None):
    if get_registration(device_id, appname, session=session):
        logger.debug(f"Got announce from registered device {device_id}.")
        return False
    logger.info(f"Registering new device '{device_id}' "
                f"of type '{appname}' from announce.")
    d = register(device_id, appname, info={}, session=session)
    return True
