from pyba.core.scripts.login import InstagramLogin


class LoginEngine:
    instagram = InstagramLogin

    @classmethod
    def available_engines(cls):
        return [name for name, value in vars(cls).items() if isinstance(value, type)]
