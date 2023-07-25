

from fastapi import APIRouter
from fastapi import Depends

from tendril.authn.users import auth_spec
from tendril.authn.users import authn_dependency
from tendril.authn.users import AuthUserModel

from tendril.config import INTERESTS_API_ENABLED
from tendril.iotedge.profiles import device_config_unified_model

from tendril.iotcore.settings import get_device_settings
from tendril.iotcore.settings import set_device_settings

from tendril.utils.db import get_session
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


device_management_router = APIRouter(
    prefix='/devices', tags=["IoT Device Hub Management API"],
    dependencies=[Depends(authn_dependency)])


@device_management_router.get("/{id}/settings",
                              response_model=device_config_unified_model)
async def read_device_settings(id: int,
                               user: AuthUserModel = auth_spec(scopes=['device:read'])):
    with get_session() as session:
        return get_device_settings(id=id, auth_user=user,
                                   session=session).export(expand=False)


@device_management_router.post("/{id}/settings",
                               response_model=device_config_unified_model)
async def write_device_settings(id: int, settings: device_config_unified_model,
                                user: AuthUserModel = auth_spec(scopes=['device:write'])):
    with get_session() as session:
        result = set_device_settings(id=id, settings=settings,
                                     auth_user=user, session=session)
        return get_device_settings(id=id, auth_user=user,
                                   session=session).export(expand=False)

if INTERESTS_API_ENABLED:
    routers = [
        device_management_router
    ]
else:
    logger.info("Not creating Device Management API routers.")
    routers = []
