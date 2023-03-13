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
"""


import importlib
import networkx

from tendril.utils.versions import get_namespace_package_names

from tendril.utils import log
logger = log.get_logger(__name__, log.DEBUG)


class IoTDeviceProfilesManager(object):
    def __init__(self, prefix):
        self._prefix = prefix
        self._device_profiles = {}
        self._docs = []
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
    def device_type_names(self):
        return self._device_profiles.keys()

    def profile(self, type_name, device_id=None):
        try:
            return self._device_profiles[type_name]
        except KeyError:
            raise DeviceTypeUnrecognized(appname, device_id)

    def finalize(self):
        pass

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
