from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from .manager import IoTDeviceProfilesManager
_manager = IoTDeviceProfilesManager(prefix='tendril.iotedge.profiles')

import sys
sys.modules[__name__] = _manager
_manager.finalize()
