

import arrow

from tendril.db.models.deviceconfig import DeviceConfigurationModel
from tendril.utils.db import with_db


class DeviceProfile(object):
    appname = None
    interest_type = 'device'
    config_model = DeviceConfigurationModel

    def __init__(self, model_instance):
        self.model_instance = model_instance

    def interest(self):
        from tendril import interests
        return interests.type_codes[self.interest_type](self.model_instance)

    def report_seen(self):
        self.interest().monitor_report('last_seen', arrow.utcnow())
        self.interest().monitor_report('online', True)

    def report_status(self, status):
        self.interest().monitors_report(status)

    @with_db
    def config(self, session=None):
        session.add(self.model_instance)
        cfg = self.model_instance.config
        if not cfg:
            cfg = self.config_model()
            self.model_instance.config = cfg
            session.add(cfg)
            session.flush()
        return cfg

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.model_instance.appname} {self.model_instance.name}>"


def load(manager):
    pass
