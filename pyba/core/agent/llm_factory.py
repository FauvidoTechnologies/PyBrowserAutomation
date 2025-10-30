from typing import Tuple, Dict

from google import genai
from google.genai.types import GenerateContentConfig
from openai import OpenAI

from pyba.utils.load_yaml import load_config
from pyba.utils.prompts import system_instruction, output_system_instruction
from pyba.utils.structure import PlaywrightResponse, OutputResponseFormat

config = load_config("general")


class LLMFactory:
    """
    Class for handling different types of LLM. The supported LLMs are:

    1. OpenAI - GPT-4o, GPT-3.5-turbo
    2. VertexAI - Gemini-2.5-pro
    """

    def __init__(self, engine):
        """
        Initialise the engine parameters as given by the user

        Args;
                engine: The LLM parameters provided by the user
        """
        self.engine = engine
        self.vertexai_client = None
        self.openai_client = None

        if self.engine.provider == "openai":
            self.openai_client = self._initialize_openai_client()
        else:
            self.vertexai_client = self._initialize_vertexai_client()

    def _initialize_vertexai_client(self):
        """
        Initialises the VertexAI client using engine parameters
        """

        vertexai_client = genai.Client(
            vertexai=True, project=self.engine.vertexai_project_id, location=self.engine.location
        )

        return vertexai_client

    def _initialize_vertexai_agent(self, system_instruction: str, response_schema):
        """
        Initiaises a VertexAI agent

        Args:
                `system_instruction`: The system instruction for the agent
                `response_schema`: The response schema for the Agent
        """
        assert system_instruction is not None and response_schema is not None

        agent = self.vertexai_client.chats.create(
            model=self.engine.model,
            config=GenerateContentConfig(
                temperature=0,
                system_instruction=system_instruction,
                response_schema=response_schema,
                response_mime_type="application/json",
            ),
        )

        return agent

    def _initialize_openai_client(self):
        """
        Initialize the OpenAI client using engine parameters
        """
        openai_client = OpenAI(api_key=self.engine.openai_api_key)
        return openai_client

    def _initialize_openai_agent(self, system_instruction: str, response_schema) -> Dict:
        """
        Initialize the OpenAI agent

        Args:
                `system_instruction`: The system instruction for the agent
                `response_schema`: The response type for the agent

        Returns:
                Dictionary of the agent parameters
        """

        agent = {
            "client": self.openai_client,
            "system_instruction": system_instruction,
            "model": config["main_engine_configs"]["openai"]["model"],
            "response_format": response_schema,
        }

        return agent

    def get_agent(self) -> Tuple[str, str]:
        """
        Endpoint to return the agents depending on the LLM called for

        Returns:
                A tuple containing the main agent and the output agent for a particular provider
        """

        if self.engine.provider == "openai":
            action_agent = self._initialize_openai_agent(
                system_instruction=system_instruction, response_schema=PlaywrightResponse
            )
            output_agent = self._initialize_openai_agent(
                system_instruction=system_instruction, response_schema=PlaywrightResponse
            )
        else:
            action_agent = self._initialize_vertexai_agent(
                system_instruction=system_instruction, response_schema=PlaywrightResponse
            )
            output_agent = self._initialize_vertexai_agent(
                system_instruction=output_system_instruction, response_schema=OutputResponseFormat
            )

        return (action_agent, output_agent)
