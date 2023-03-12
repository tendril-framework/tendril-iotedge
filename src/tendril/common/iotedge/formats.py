

from typing import Pattern
from tendril.utils.pydantic import TendrilTBaseModel


class IoTDeviceIDTModel(TendrilTBaseModel):
    __root__ = Pattern['^[0-9A-F]{12}$']


class IoTDeviceAnnounceTModel(TendrilTBaseModel):
    id: IoTDeviceIDTModel
    appname: str
