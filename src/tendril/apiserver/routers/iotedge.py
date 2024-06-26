

from fastapi import APIRouter
from fastapi import Depends
from fastapi import BackgroundTasks
from fastapi import File
from fastapi import UploadFile

from tendril.common.iotedge.formats import IoTDevicePingTModel
from tendril.common.iotedge.formats import IoTDeviceAnnounceTModel
from tendril.common.iotedge.formats import IoTDeviceAnnounceResponseTModel
from tendril.common.iotedge.formats import IoTDeviceSettingRequestTModel
from tendril.iotedge.profiles import device_config_unified_model

from tendril.authn.users import auth_spec
from tendril.authn.users import AuthUserModel
from tendril.authn.users import authn_dependency

from tendril.iotedge.announce import announce_device
from tendril.iotedge.heartbeat import ping
from tendril.iotedge.config import get_config
from tendril.iotedge.logs import publish_logs

from tendril.config import IOTEDGE_API_ENABLED
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


iotedge_reports_router = APIRouter(prefix='/iot/report',
                                   tags=["IOT Device Edge Reporting API"],
                                   dependencies=[Depends(authn_dependency),
                                                 auth_spec()])


@iotedge_announce_router.post("/announce",
                              response_model=IoTDeviceAnnounceResponseTModel)
async def iot_device_announce(announce: IoTDeviceAnnounceTModel,
                              background_tasks: BackgroundTasks):
    return announce_device(device_id=announce.id,
                           appname=announce.appname,
                           have_credentials=announce.have_credentials,
                           device_sysinfo=announce.sysinfo,
                           background_tasks=background_tasks)


@iotedge_router.post("/ping")
async def iot_device_ping(message: IoTDevicePingTModel,
                          background_tasks: BackgroundTasks):
    result = ping(device_id=message.id, status=message.status,
                  background_tasks=background_tasks)
    return 'pong'


@iotedge_router.post("/settings", response_model=device_config_unified_model)
async def iot_device_settings(req: IoTDeviceSettingRequestTModel):
    result = get_config(device_id=req.id, appname=req.appname)
    return result


@iotedge_router.post("/logs")
async def iot_device_publish_logs(background_tasks: BackgroundTasks,
                                  file: UploadFile = File(...),
                                  user: AuthUserModel = auth_spec()):
    device_id = user.email.split('@')[0]
    response = await publish_logs(device_id=device_id, logs_archive=file,
                                  background_tasks=background_tasks)
    return response


routers = []


if IOTEDGE_API_ENABLED:
    routers.extend([
        iotedge_announce_router,
        iotedge_router,
        iotedge_reports_router
    ])
else:
    logger.info("Not creating IoTEdge API routers.")
