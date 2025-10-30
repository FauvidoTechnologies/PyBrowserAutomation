from pyba.utils.exceptions import ServiceNotSelected, ServerLocationUndefined
from pyba.utils.load_yaml import load_config

config = load_config("general")["main_engine_configs"]


class Provider:
    """
    Class to handle the provider instances.
    """

    def __init__(
        self,
        openai_api_key: str = None,
        vertexai_project_id: str = None,
        vertexai_server_location: str = None,
        logger=None,
    ):
        """
        Args:
                openai_api_key: API key for OpenAI models should you want to use that
                vertexai_project_id: Create a VertexAI project to use that instead of OpenAI
                vertexai_server_location: VertexAI server location
                logger: The logger instance
        """

        self.provider: str | None = None
        self.model: str | None = None
        self.openai_api_key: str | None = openai_api_key
        self.vertexai_project_id: str | None = vertexai_project_id
        self.location: str | None = vertexai_server_location

        self.log = logger

        self.handle_keys()

    def handle_keys(self):
        if self.openai_api_key is None and self.vertexai_project_id is None:
            raise ServiceNotSelected()

        if self.vertexai_project_id and self.location is None:
            raise ServerLocationUndefined(self.location)

        if self.openai_api_key and self.vertexai_project_id:
            self.log.warning(
                "You've defined both vertexai and openai models, we're choosing to go with openai!"
            )
            self.provider = config["openai"]["provider"]
            self.vertexai_project_id = None
            self.location = None

        elif self.vertexai_project_id:
            # Assuming that we don't have an openai_api_key
            self.provider = config["vertexai"]["provider"]
            self.model = config["vertexai"]["model"]
        else:
            self.provider = config["openai"]["provider"]
