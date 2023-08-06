

from functools import wraps

from .registration import registered_device

from tendril.utils.db import with_db
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


@with_db
@registered_device()
def ping(device=None, appname=None, status=None,
         background_tasks=None, session=None):
    logger.info(f"Got ping from {device}")
    device.report_seen(background_tasks=background_tasks)
    device.report_status(status, background_tasks=background_tasks)
