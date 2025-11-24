from typing import Dict

from pydantic import BaseModel

from pyba.core.agent.base_agent import BaseAgent


class ExtractionAgent(BaseAgent):
    """
    Defines the Extraction Agent functions. This is a helper module along with the
    output agent, no more only final answers.

            Intermediate answers as well!

        Args:
        `extraction_format`: The format which should be fitted


    The class exposes an async function and won't hinder the main pipeline's flow.
    """

    def __init__(self, extraction_format: BaseModel):
        super().__init__()  # Initialising the base params from BaseAgent

        self.extraction_format = extraction_format
        self.agent = self.llm_factory.get_extraction_agent(
            extraction_format=self.extraction_format
        )  # Getting the extraction agent

    async def extract_information(self, page_contents: Dict[str, str]):
        """
        Function to fit the `extraction_format`

        Args:
                `page_contents`: The contents of the page the model is currently seeing

        The sync endpoint will be blocking.
        """
        pass
