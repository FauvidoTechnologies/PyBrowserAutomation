from pydantic import BaseModel

from pyba.core.agent.base_agent import BaseAgent
from pyba.utils.prompts.extraction_prompts import general_prompt


class ExtractionAgent(BaseAgent):
    """
    This is a helper agent in all aspects. To use this, all other agents
    need to import and initialise this.

    This agent allows for threaded infomation extraction to not hinder the main pipeline flow.

    Args:
        `extraction_format`: The format which should be fitted for the extraction
    """

    def __init__(self, engine, extraction_format: BaseModel):
        super().__init__(engine=engine)  # Initialising the base params from BaseAgent

        self.extraction_format = extraction_format
        self.agent = self.llm_factory.get_extraction_agent(
            extraction_format=self.extraction_format
        )  # Getting the extraction agent

    def _initialise_prompt(self, task: str, actual_text: str):
        """
        Takes in the actual_text and wraps it around the general prompt

        Args:
                `task`: The user's defined task
                `actual_text`: The current text on the page
        """
        return general_prompt.format(task=task, actual_text=actual_text)

    def run_threaded_info_extraction(self, task: str, actual_text: str):
        """
        Threaded function to extract data from the current page

        Args:
                        `task`: The user's defined task
            `actual_text`: The current page text
        """

        pass
