from playwright.async_api import Page
from pyba.core.scripts.extractions.general import GeneralDOMExtraction
from pyba.core.scripts.extractions.youtube_ import YouTubeDOMExtraction

import asyncio


class ExtractionEngines:
    """
    Returns all the extraction engines and provides a way to get their names
    """

    general = GeneralDOMExtraction
    youtube = YouTubeDOMExtraction

    @classmethod
    def available_engines(cls):
        return [name for name, value in vars(cls).items() if isinstance(value, type)]

    def __init__(self, html: str, body_text: str, elements: list, base_url: str, page: Page):
        self.html = html
        self.body_text = body_text
        self.elements = elements
        self.base_url = base_url
        self.page = page

        self.output = {}

    async def extract_all(self):
        """
        Create the all encompassing extraction engine
        """
        general = ExtractionEngines.general(
            html=self.html,
            body_text=self.body_text,
            elements=self.elements,
            base_url=self.base_url,
        )
        general_output = await general.extract()
        self.output = general_output

        youtube = ExtractionEngines.youtube(page=self.page)

        if "youtube.com" in self.page.url:
            # Usually the dom extraction is pretty fast but the videos take some time to load up in the javascript
            # Hence a small wait here helps in loading that
            await asyncio.sleep(3)
            youtube_output = await youtube.extract()
            self.output.youtube = youtube_output

        return self.output
