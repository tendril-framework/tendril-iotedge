

from functools import wraps
from tendril import interests
from tendril.db.controllers.interests import get_interest

from tendril.common.iotedge.exceptions import DeviceTypeUnrecognized
from tendril.common.iotedge.exceptions import DeviceTypeMismatch

from . import profiles

from tendril.utils.db import with_db
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


@with_db
def get_registration(device_id, appname=None, session=None):
    if appname:
        profile = profiles.profile(appname, device_id=device_id)
        interest = get_interest(name=device_id, type=profile.interest_type,
                                raise_if_none=False, session=session)
    else:
        interest = get_interest(name=device_id, raise_if_none=False,
                                session=session)
        appname = interest.appname
        profile = profiles.profile(appname, device_id=device_id)

    if not interest:
        return None

    if appname and interest.appname != appname:
        raise DeviceTypeMismatch(appname, interest.appname, device_id)

    return profile(interest)


@with_db
def register(device_id, appname, info={}, session=None):
    profile = profiles.profile(appname, device_id=device_id)
    itype = interests.type_codes[profile.interest_type]
    interest = itype(name=device_id, appname=appname, info=info,
                     must_create=True, session=session)
    return profile(interest)


def registered_device(appname=None):
    def decorator(func):
        @wraps(func)
        def get_registered_device(device_id=None, session=None, **kwargs):
            if appname:
                device = get_registration(device_id, appname=appname, session=session)
            else:
                device = get_registration(device_id, session=session)
                kwargs['appname'] = device.appname
            return func(device=device, session=session, **kwargs)
        return get_registered_device
    return decorator
