

import arrow

from tendril.db.models.deviceconfig import DeviceConfigurationModel
from tendril.utils.db import with_db
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


class DeviceProfile(object):
    appname = None
    interest_type = 'device'
    config_model = DeviceConfigurationModel

    def __init__(self, model_instance):
        self._model_instance = model_instance

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
