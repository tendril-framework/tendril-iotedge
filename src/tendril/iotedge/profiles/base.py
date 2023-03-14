

from sqlalchemy.orm.exc import NoResultFound
from tendril.db.models.deviceconfig import DeviceConfigurationModel
from tendril.utils.db import with_db


class DeviceProfile(object):
    appname = None
    interest_type = 'device'
    config_model = DeviceConfigurationModel

    def __init__(self, interest):
        self.interest = interest

    @with_db
    def config(self, session=None):
        session.add(self.interest.model_instance)
        cfg = self.interest.model_instance.config
        if not cfg:
            cfg = self.config_model()
            self.interest.model_instance.config = cfg
            session.add(cfg)
            session.flush()
        return cfg

    def __repr__(self):
        return f"<{self.interest.appname} {self.interest.name}>"


def load(manager):
    pass
