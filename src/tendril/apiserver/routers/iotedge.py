

from fastapi import APIRouter
from fastapi import Depends

from tendril.common.iotedge.formats import IoTDeviceIDTModel
from tendril.common.iotedge.formats import IoTDevicePingTModel
from tendril.common.iotedge.formats import IoTDeviceAnnounceTModel
from tendril.common.iotedge.formats import IoTDeviceAnnounceResponseTModel

from tendril.authn.users import auth_spec
from tendril.authn.users import authn_dependency
from tendril.authn.users import AuthUserModel

from tendril.iotedge.announce import announce_device
from tendril.iotedge.heartbeat import ping

from tendril.config import IOTEDGE_ENABLED
from tendril.config import IOTEDGE_ANNOUNCE_ENDPOINT_OPEN

from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


if IOTEDGE_ANNOUNCE_ENDPOINT_OPEN:
    kwargs = {}
else:
    kwargs = {
        'dependencies': [Depends(authn_dependency)]
    }

iotedge_announce_router = APIRouter(prefix='/iot', **kwargs,
                                    tags=['IOT Device Edge Announce API'])

iotedge_router = APIRouter(prefix='/iot',
                           tags=["IOT Device Edge Core API"],
                           dependencies=[Depends(authn_dependency),
                                         auth_spec()])


@iotedge_announce_router.post("/announce",
                              response_model=IoTDeviceAnnounceResponseTModel)
async def iot_device_announce(announce: IoTDeviceAnnounceTModel):
    return announce_device(device_id=announce.id,
                              appname=announce.appname,
                              have_credentials=announce.have_credentials)


@iotedge_router.post("/ping")
async def iot_device_ping(message: IoTDevicePingTModel):
    result = ping(device_id=message.id, status=message.status)
    return 'pong'


if IOTEDGE_ENABLED:
    routers = [
        iotedge_announce_router,
        iotedge_router
    ]
else:
    logger.info("Not creating IoTEdge API routers.")
    routers = []
