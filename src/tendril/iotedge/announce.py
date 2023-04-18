

from tendril.caching import transit
from tendril.common.states import LifecycleStatus

from .registration import get_registration
from .registration import register

from tendril.utils.db import with_db
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


@with_db
def announce_device(device_id, appname, have_credentials, session=None):
    # TODO Handle other device lifecycle states
    rv = {}
    device = get_registration(device_id, appname, session=session)
    if device:
        logger.debug(f"Got announce from a registered device {device_id} "
                     f"in state {device.model_instance.status}.")
        if device.model_instance.status == LifecycleStatus.ACTIVE:
            if not have_credentials:
                # If there is a password waiting for one-time transmission,
                # transmit it.
                password = transit.read(namespace="ott:dp", key=device_id)
                if not password:
                    logger.warning(f"Active registered device {device_id} does not have a token")
                    # If there is no password waiting for one-time transmission,
                    # some user should check the request is not spurious, and then
                    # manually reset password and load it up for one-time transmission.
                    # Raise manual password reset request here. Changing device status to
                    # NEW should get the job done as presently implemented.
                else:
                    logger.info(f"Found password for {device_id} on transit cache.")
                    transit.delete(namespace="ott:dp", key=device_id)
                    rv['password'] = password
        if device.model_instance.status in [LifecycleStatus.NEW, LifecycleStatus.APPROVAL]:
            # We're waiting for activation and don't need to do anything here.
            pass
    else:
        logger.info(f"Registering new device '{device_id}' "
                    f"of type '{appname}' from announce.")
        if have_credentials:
            logger.warning(f"Unregistered device {device_id} seems to already have a token")
            # Raise some kind of error here. The device might need to checked for compromise.
        device = register(device_id, appname, info={}, session=session)
        # When the device is activated, the interest activation will create a password
        # and store it on transit for one time transmission within this endpoint itself.
    rv.update({
        'interest_id': device.model_instance.id,
        'id': device.model_instance.name,
        'status': device.model_instance.status
    })
    return rv
