

from tendril.libraries import interests
from tendril.common.interests.exceptions import InterestTypeUnsupported

from tendril.utils.db import with_db
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


@with_db
def get_device_settings(id: int, auth_user=None, session=None):
    library = interests.find_library(id)
    interest = library.item(id=id, session=session)
    if not hasattr(interest, 'appname'):
        raise InterestTypeUnsupported("'appname' attribute", id=id, name=interest.name)
    profile = interest.profile(auth_user=auth_user, session=session)
    return profile.config(session=session)


@with_db
def set_device_settings(id: int, settings=None, auth_user=None, session=None):
    library = interests.find_library(id)
    interest = library.item(id=id, session=session)
    if not hasattr(interest, 'appname'):
        raise InterestTypeUnsupported("'appname' attribute", id=id, name=interest.name)
    return interest.configure(settings=settings, auth_user=auth_user, session=session)
