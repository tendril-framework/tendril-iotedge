

from functools import wraps

from .registration import registered_device

from tendril.utils.db import with_db
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


def mark_seen(func):
    @wraps(func)
    def inner(device=None, appname=None, session=None, **kwargs):
        logger.debug(f"Mark device {device} as seen")
        func(device=device, session=session, **kwargs)
    return inner


@with_db
@registered_device()
@mark_seen
def ping(device=None, appname=None, status=None, session=None):
    logger.info(f"Got ping from {device}")
