

from tendril.core.mq.aio import with_mq_client
from tendril.utils import log
logger = log.get_logger(__name__)


@with_mq_client('X')
async def create_mq_topology(mq=None):
    logger.info("Creating the Device Communications queue.")
    device_aggregation_queue = await mq.create_work_queue('device_aggregation', topic='device.from.*')
