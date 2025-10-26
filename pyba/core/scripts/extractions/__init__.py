from pyba.core.scripts.extractions.general import GeneralDOMExtraction
from pyba.core.scripts.extractions.youtube_ import YouTubeDOMExtraction


class ExtractionEngines:
    """
    Returns all the extraction engines and provides a way to get their names
    """

    general = GeneralDOMExtraction
    youtube = YouTubeDOMExtraction

    @classmethod
    def available_engines(cls):
        return [name for name, value in vars(cls).items() if isinstance(value, type)]
