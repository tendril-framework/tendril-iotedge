

import os
import datetime
from tendril.caching import tokens

from .registration import registered_device

from tendril.common.exceptions import FileTypeNotSupportedException
from tendril.utils.db import with_db
from tendril.utils import log
logger = log.get_logger(__name__)


@with_db
@registered_device()
async def publish_logs(logs_archive, device=None, appname=None,
                       background_tasks=None, session=None):
    logger.info(f"Got logs from {device}")
    file_name, file_ext = os.path.splitext(logs_archive.filename)
    if file_ext not in ['.zip']:
        raise FileTypeNotSupportedException

    device_name = device.model_instance.name
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    storage_filename = f"{device_name}.{ts}.logs{file_ext}"

    upload_token = tokens.open(
        namespace='dlu',
        metadata={'device': device_name,
                  'filename': storage_filename},
        current="Request Created",
        progress_max=1, ttl=600,
    )

    background_tasks.add_task(
        device.receive_logs, file=logs_archive,
        rename_to=storage_filename, token_id=upload_token.id,
        session=session
    )

    return upload_token

