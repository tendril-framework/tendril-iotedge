

from tendril.utils.db import with_db

from .registration import registered_device

from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


@with_db
@registered_device()
def get_config(device=None, appname=None, session=None):
    config = device.config(session=session)
    logger.info(f"Sending device settings to {device}")
    return config.export()
