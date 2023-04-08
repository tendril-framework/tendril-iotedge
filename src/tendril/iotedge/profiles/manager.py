#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2019-2023 Chintalagiri Shashank
#
# This file is part of tendril.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Tendril IoT Device Profiles Manager (:mod:`tendril.iotedge.profiles.manager`)
=============================================================================

<< Consider moving Device Profiles to iotcore or iotcommon. Presently,
   iotedge is the foundational package for the tendril-iot stack. >>
"""


import importlib
from typing import Union
from pydantic import Field
from typing_extensions import Annotated

from tendril.utils.versions import get_namespace_package_names
from tendril.iotedge.profiles.base import DeviceConfigurationModel
from tendril.common.iotedge.exceptions import DeviceTypeUnrecognized

from tendril.utils import log
logger = log.get_logger(__name__, log.DEBUG)


class IoTDeviceProfilesManager(object):
    def __init__(self, prefix):
        self._prefix = prefix
        self._device_profiles = {}
        self._docs = []
        self.device_config_unified_model = None
        self._load_profiles()

    def _load_profiles(self):
        logger.info("Loading device profiles from {0}".format(self._prefix))
        modules = list(get_namespace_package_names(self._prefix))
        for m_name in modules:
            if m_name in [__name__, f"{self._prefix}.db", f"{self._prefix}.template"]:
                continue
            m = importlib.import_module(m_name)
            m.load(self)
        logger.info("Done loading device profiles from {0}".format(self._prefix))

    def register_device_profile(self, name, profile, doc=None):
        logger.info(f"Registering <{profile.__name__}> to handle IoT Devices of type '{name}'")
        self._device_profiles[name] = profile
        self._docs.append((name, doc))

    @property
    def device_profiles(self):
        return self._device_profiles

    @property
    def device_appnames(self):
        return self._device_profiles.keys()

    @property
    def device_config_tmodels(self):
        return {x.appname: x.config_model.tmodel() for x in self._device_profiles.values()}

    def profile(self, appname, device_id=None):
        try:
            return self._device_profiles[appname]
        except KeyError:
            raise DeviceTypeUnrecognized(appname, device_id)

    def finalize(self):
        logger.info("Building device configuration message models")
        if len(self.device_profiles) > 1:
            self.device_config_unified_model = \
                Annotated[Union[tuple(self.device_config_tmodels.values())],
                          Field(discriminator='appname')]
        elif len(self.device_profiles) == 1:
            self.device_config_unified_model = \
                list(self._device_profiles.values())[0].config_model.tmodel()
        else:
            self.device_config_unified_model = DeviceConfigurationModel.tmodel()

    def __getattr__(self, item):
        if item == '__file__':
            return None
        if item == '__path__':
            return None
        if item == '__len__':
            return len(self._types.keys())
        if item == '__all__':
            return list(self._types.keys()) + \
                   ['doc_render']
        return self._device_profiles[item]

    def doc_render(self):
        return self._docs

    def __repr__(self):
        return "<IoTDeviceProfilesManager>"
