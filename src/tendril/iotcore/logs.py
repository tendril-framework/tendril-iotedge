

from tendril.libraries import interests
from tendril.common.interests.exceptions import InterestTypeUnsupported
from tendril.artefacts.db.controller import get_interest_artefacts
from tendril.filestore.db.model import StoredFileModel

from tendril.utils.db import with_db
from tendril.utils import log
logger = log.get_logger(__name__)


@with_db
def request_device_logs(id: int, background_tasks=None, auth_user=None, session=None):
    library = interests.find_library(id)
    interest = library.item(id=id, session=session)
    if not hasattr(interest, 'appname'):
        raise InterestTypeUnsupported("'appname' attribute", id=id, name=interest.name)
    interest.trigger_device_publish_logs(background_tasks=background_tasks)
    return 'OK'


@with_db
def available_device_logs(id: int, background_tasks=None, auth_user=None, session=None):
    library = interests.find_library(id)
    interest = library.item(id=id, session=session)
    if not hasattr(interest, 'appname'):
        raise InterestTypeUnsupported("'appname' attribute", id=id, name=interest.name)

    log_files = get_interest_artefacts(interest_id=interest.id,
                                       type=StoredFileModel,
                                       label="device_logs",
                                       session=session)

    return log_files
