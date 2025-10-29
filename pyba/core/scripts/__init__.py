# Imports for the extraction scripts
from pyba.core.scripts.extractions import ExtractionEngines

# Imports for the login scripts
from pyba.core.scripts.login import InstagramLogin, FacebookLogin, GmailLogin


class LoginEngine:
    """
    Makes the Automated Login engines available to the main program
    """

    instagram = InstagramLogin
    facebook = FacebookLogin
    gmail = GmailLogin

    @classmethod
    def available_engines(cls):
        return [name for name, value in vars(cls).items() if isinstance(value, type)]
