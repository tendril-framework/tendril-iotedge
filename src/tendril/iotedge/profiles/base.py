

class DeviceProfile(object):
    appname = None
    interest_type = 'device'

    def __init__(self, interest):
        self.interest = interest

    def __repr__(self):
        return f"<{self.interest.appname} {self.interest.name}>"


def load(manager):
    pass
