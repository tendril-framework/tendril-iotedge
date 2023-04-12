

from typing import Literal
from typing import Optional
from tendril.utils.pydantic import TendrilTBaseModel
from tendril.common.states import LifecycleStatus


IoTDeviceIDTModel = str
IoTDeviceAppnameTModel = str


class IoTDeviceMessageTModel(TendrilTBaseModel):
    id: IoTDeviceIDTModel


class IoTDeviceAnnounceTModel(IoTDeviceMessageTModel):
    appname: IoTDeviceAppnameTModel
    have_credentials: bool


class IoTDevicePingTModel(IoTDeviceMessageTModel):
    status: Optional[dict]


class IoTDeviceAnnounceResponseTModel(IoTDeviceMessageTModel):
    status: LifecycleStatus
    interest_id: int
    password: Optional[str]


class IoTDeviceSettingRequestTModel(IoTDeviceMessageTModel):
    appname: IoTDeviceAppnameTModel
