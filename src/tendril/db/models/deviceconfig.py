

from typing import Union
from typing import Literal
from typing import Optional
from pydantic import create_model
from functools import lru_cache
from collections import namedtuple
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from tendril.utils.pydantic import TendrilTBaseModel
from tendril.utils.db import DeclBase
from tendril.utils.db import BaseMixin
from tendril.utils.db import TimestampMixin


# TODO
#  For the moment, this package and the sxm-core implementation holds the set of
#  api endpoints and other assets which will be needed to build a backend settings
#  management API.
#  This might make the code separation a little more complicated than needed, so an
#  alternate refactoring might be suitable. For instance, such a heavy implementaion
#  of the DeviceConfigurationModel is not in line with the typical tendril
#  architecture. The assumption that there will be a "Device" intterest class with the
#  "DeviceModel" table is not good either.
#  Specifically, tendril-iotedge as presently written is not independently viable,
#  and in fact is not viable even when combined with more fundamental tendril packages.
#  It includes a great number of implicit dependencies on the downstream instance
#  implementation package which need to be better resolved.
#  These assets will be written to be generic to the extent
#  possible, until they reach critical mass and can perhaps be moved into a
#  distributable package of their own. Tentatively, tendril-iotcore, holding most
#  of the separable device related bulk from sxm-core.

cfg_option_spec = namedtuple('CfgOptionSpec', ['description', 'accessor',
                                               'exporter', 'export_tmodel',
                                               'validator', 'type', 'default', 'read_only'],
                             defaults=[None, None,
                                       None, str, None, False])


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

    @classmethod
    @lru_cache(maxsize=None)
    def configuration_spec(cls):
        return {'appname': cfg_option_spec("Device Application Name", 'appname', read_only=True)}

    @classmethod
    def _build_tmodel(cls, name, spec, base=TendrilTBaseModel):
        # WARNING : This is an exercise in extreme fragility. And shooting yourself in the foot.
        #  Do NOT replicate this approach until this is stable and comfortable.
        components = {}
        for key, lspec in spec.items():
            if isinstance(lspec, cfg_option_spec):
                if key=='appname':
                    components[key] = (Literal[cls.device_type], cls.device_type)
                else:
                    if lspec.exporter and lspec.export_tmodel:
                        components[key] = (Optional[Union[lspec.type, lspec.export_tmodel]], None)
                    else:
                        components[key] = (Optional[lspec.type], None)
            elif isinstance(lspec, dict):
                subname = key
                subname = subname.replace('_', ' ')
                subname = subname.replace('-', ' ')
                parts = subname.split(' ')
                parts = [x.capitalize() for x in parts]
                subname = ''.join(parts)
                subname = name.replace("TModel", f"{subname}TModel")
                components[key] = (Optional[cls._build_tmodel(subname, lspec, base=base)], None)
            else:
                raise TypeError(f"Got an unsupported type for device option spec {lspec}")
        return create_model(name, **components, __base__=base)

    @classmethod
    @lru_cache(maxsize=None)
    def tmodel(cls):
        name = cls.__name__.replace("Model", "TModel")
        return cls._build_tmodel(name, cls.configuration_spec())

    def _extract_config(self, spec, expand=True):
        rv = {}
        for key, lspec in spec.items():
            if isinstance(lspec, dict):
                rv[key] = self._extract_config(lspec, expand=expand)
            elif isinstance(lspec, cfg_option_spec):
                if expand and lspec.exporter:
                    rv[key] = getattr(self, lspec.exporter)(getattr(self, lspec.accessor))
                else:
                    rv[key] = getattr(self, lspec.accessor)
            else:
                raise TypeError(f"Got an unsupported type for device option spec {lspec}")
        return rv

    def export(self, expand=True):
        return self._extract_config(self.configuration_spec(), expand=expand)
