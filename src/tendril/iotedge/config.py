

from .registration import registered_device
from tendril.utils.db import with_db
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


@with_db
@registered_device()
@mark_seen
def get_config(device=None, appname=None, session=None):
    return device.config
