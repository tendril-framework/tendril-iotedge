

from fastapi import APIRouter
from fastapi import Depends

from tendril.common.iotedge.formats import IoTDeviceAnnounceTModel

from tendril.authn.users import auth_spec
from tendril.authn.users import authn_dependency
from tendril.authn.users import AuthUserModel

from tendril.config import IOTEDGE_ENABLED
from tendril.config import IOTEDGE_ANNOUNCE_ENDPOINT_OPEN


if IOTEDGE_ANNOUNCE_ENDPOINT_OPEN:
    kwargs = {}
else:
    kwargs = {
        'dependencies': [Depends(authn_dependency)]
    }

iotedge_announce_router = APIRouter(prefix='/iot', **kwargs,
                                    tags=['IOT Device Edge Announce API'])

iotedge_router = APIRouter(prefix='/iot',
                           tags=["IOT Device Edge Core API"])


@iotedge_announce_router.post("/announce")
async def announce_device(announce: IoTDeviceAnnounceTModel):
    print(announce)


if IOTEDGE_ENABLED:
    routers = [
        iotedge_announce_router,
        iotedge_router
    ]
else:
    routers = []
