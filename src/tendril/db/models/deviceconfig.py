

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from tendril.utils.db import DeclBase
from tendril.utils.db import BaseMixin
from tendril.utils.db import TimestampMixin


class DeviceConfigurationModel(DeclBase, BaseMixin, TimestampMixin):
    device_type = "device"
    appname = Column(String(50), nullable=False, default=device_type)
    hname = Column(String(100))

    @declared_attr
    def devices(cls):
        return relationship("DeviceModel", back_populates='config', lazy='selectin')

    __mapper_args__ = {
        "polymorphic_identity": device_type,
        "polymorphic_on": appname
    }
