from pyba.core.scripts.login import InstagramLogin, FacebookLogin


class LoginEngine:
    instagram = InstagramLogin
    facebook = FacebookLogin

    @classmethod
    def available_engines(cls):
        return [name for name, value in vars(cls).items() if isinstance(value, type)]
