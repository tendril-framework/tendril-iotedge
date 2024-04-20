

import os
import arrow
from httpx import HTTPStatusError
from asgiref.sync import async_to_sync
from tendril.filestore import buckets
from tendril.config import IOTEDGE_DEVICE_LOGS_UPLOAD_FILESTORE_BUCKET

from tendril.caching import tokens
from tendril.caching.tokens import TokenStatus
from tendril.db.models.deviceconfig import DeviceConfigurationModel
from tendril.utils.db import with_db
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


class DeviceProfile(object):
    appname = None
    interest_type = 'device'
    config_model = DeviceConfigurationModel
    logs_upload_bucket_name = IOTEDGE_DEVICE_LOGS_UPLOAD_FILESTORE_BUCKET

    def __init__(self, model_instance):
        self._model_instance = model_instance

    @property
    def upload_bucket(self):
        if not hasattr(self, '_logs_upload_bucket'):
            self._logs_upload_bucket = None
        if not self._logs_upload_bucket:
            self._logs_upload_bucket = buckets.get_bucket(self.logs_upload_bucket_name)
        return self._logs_upload_bucket

    @property
    def model_instance(self):
        return self._model_instance

    def interest(self):
        from tendril import interests
        itype = interests.type_codes[self.interest_type]
        if isinstance(self.model_instance, itype):
            return self.model_instance
        rv = itype(self.model_instance)
        return rv

    def report_seen(self, background_tasks=None):
        self.interest().monitor_report('last_seen', arrow.utcnow(), background_tasks=background_tasks)
        self.interest().monitor_report('online', True, background_tasks=background_tasks)

    def report_status(self, status, background_tasks=None):
        self.interest().monitors_report(status,
                                        background_tasks=background_tasks)

    def _report_filestore_error(self, token_id, e, action_comment):
        logger.warn(f"Exception while {action_comment} : HTTP {e.response.status_code} {e.response.text}")
        if token_id:
            tokens.update(
                'dlu', token_id, state=TokenStatus.FAILED,
                error={"summary": f"Exception while {action_comment}",
                       "filestore": {
                           "code": e.response.status_code,
                           "content": e.response.json()}
                       }
            )

    @with_db
    def receive_logs(self, file, rename_to=None, token_id=None, session=None):
        # TODO Consider integrating this into a standardized upload handler
        #  in the interest itself
        storage_folder = f'{self.model_instance.id}'
        if token_id:
            tokens.update('dlu', token_id,
                          state=TokenStatus.INPROGRESS, max=2,
                          current="Uploading File to Filestore")

        filename = rename_to or file.filename

        # 2. Upload File to Bucket
        try:
            upload_response =  async_to_sync(self.upload_bucket.upload)(
                file=(os.path.join(storage_folder, filename), file.file),
                interest=self.model_instance.id, label="device_logs"
            )
        except HTTPStatusError as e:
            self._report_filestore_error(token_id, e, "uploading device logs file to bucket")
            return

        if token_id:
            tokens.update('dlu', token_id, current="Finishing",  done=2,
                          metadata={'storedfile_id': upload_response['storedfileid']}, )

        # 7. Close Upload Ticket
        tokens.close('dlu', token_id)

    @with_db
    def config(self, session=None):
        if hasattr(self.model_instance, 'model_instance'):
            logger.warn("model_instance is set to something that isn't a model instance.")
            model_instance = self.model_instance.model_instance
        else:
            model_instance = self.model_instance
        session.add(model_instance)
        cfg = model_instance.config
        if not cfg:
            cfg = self.config_model()
            model_instance.config = cfg
            session.add(cfg)
            session.flush()
        return cfg

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.model_instance.appname} {self.model_instance.name}>"


def load(manager):
    pass
