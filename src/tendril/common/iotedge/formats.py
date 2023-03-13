

from typing import Pattern
from typing import Optional
from tendril.utils.pydantic import TendrilTBaseModel
from tendril.common.interests.states import InterestLifecycleStatus


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
    status: InterestLifecycleStatus
    interest_id: int
    password: Optional[str]
