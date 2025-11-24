from typing import Dict

from pydantic import BaseModel

from pyba.core.agent.base_agent import BaseAgent


class ExtractionAgent(BaseAgent):
    """
    Defines the Extraction Agent functions. This is a helper module along with the
    output agent, no more only final answers.

            Intermediate answers as well!
    """

    def __init__(self):
        super().__init__()  # Initialising the base params from BaseAgent

    async def extract_information(
        self, extraction_format: BaseModel, page_contents: Dict[str, str]
    ):
        """
        Function to fit the `extraction_format`

        Args:
                `extraction_format`: The format which should be fitted
                `page_contents`: The contents of the page the model is currently seeing

        This is an async function and won't hinder the main pipeline's flow. Note that to use this,
        you will have to run the async endpoint.

        The sync endpoint will be blocking.
        """
        pass
