from config.config import Config


class BaseThirdPartyServices:
    def __init__(self, config: Config):
        self.config = config
