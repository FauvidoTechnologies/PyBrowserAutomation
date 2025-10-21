import sys

from playwright.async_api import async_playwright

from pyba.core.agent.playwright_agent import PlaywrightAgent
from pyba.core.lib import DOMExtraction, HandleDependencies
from pyba.core.lib.action import perform_action
from pyba.utils.exceptions import PromptNotPresent, ServiceNotSelected, ServerLocationUndefined


class Engine:
    """
    The main entrypoint for browser automation. This engine exposes the main entry point which is the run() method
    """

    def __init__(
        self,
        openai_api_key: str = None,
        vertexai_project_id: str = None,
        vertexai_server_location: str = None,
        headless: bool = False,
        handle_dependencies: bool = True,
    ):
        """
        1. Get the keys
        2. Check if we are to run in the headless mode (default at No)
        3. Does the user need us to download dependencies (default at Yes)
        """
        self.provider = None
        self.headless_mode = headless

        selectors = (
            "input:not([type='hidden']):not([type='submit']):not([type='button']):not([type='reset']):not([type='file'])",
            "textarea",
            "select",
            "[contenteditable='true']",
            "[role='textbox']",
            "[role='searchbox']",
            "[role='combobox']",
        )
        self.combined_selector = ", ".join(selectors)

        if handle_dependencies:
            HandleDependencies.playwright.handle_dependencies()

        if openai_api_key is None and vertexai_project_id is None:
            raise ServiceNotSelected()

        if vertexai_project_id and vertexai_server_location is None:
            raise ServerLocationUndefined(vertexai_server_location)

        if openai_api_key and vertexai_project_id:
            print(
                "You've defined both vertexai and openai models, we're choosing to go with openai!"
            )
            self.openai_api_key = openai_api_key
            self.provider = "openai"

        if vertexai_project_id:
            # Assuming that we don't have an openai_api_key
            self.provider = "vertexai"
            self.vertexai_project_id = vertexai_project_id
            self.location = vertexai_server_location
            self.model = "gemini-2.5-pro"  # Keeping this as fixed
        else:
            self.provider = "openai"
            self.openai_api_key = openai_api_key

        # Defining the playwright agent with the defined configs
        self.playwright_agent = PlaywrightAgent(engine=self)  # This is amusing

    async def run(self, prompt: str = None):
        """
        The most basic implementation for the run function

        Args:
            `prompt`: The user's instructions
                Right now we're assuming that the user's prompt is well defined. In later
                versions we'll come up with a fix for that as well.
        """

        if prompt is None:
            raise PromptNotPresent()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            cleaned_dom = {
                "hyperlinks": None,
                "input_fields": None,
                "clickable_fields": None,
                "actual_text": None,
                "current_url": None,
            }

            for steps in range(0, 10):
                # Say we're going to run only 10 steps so far, so after this no more automation
                # Get an actionable PlaywrightResponse from the models
                action = self.playwright_agent.process_action(
                    cleaned_dom=cleaned_dom, user_prompt=prompt
                )

                if all(value is None for value in vars(action).values()):
                    # This means the goal has been achieved
                    print("Automated completed, agent returned None")
                    sys.exit(0)

                print(f"\n\nThis is the action: {action}\n\n")
                # If its not None, then perform it
                await perform_action(page, action)

                page_html = await page.content()
                body_text = await page.inner_text("body")
                elements = await page.query_selector_all(self.combined_selector)
                base_url = page.url

                # Then we need to extract the new cleaned_dom from the page
                extractionEngine = DOMExtraction(
                    html=page_html, body_text=body_text, elements=elements, base_url=base_url
                )

                # Passing in known_fields for the input fields that we already know off so that
                # its easier for the extraction engine to work
                cleaned_dom = await extractionEngine.extract()

                cleaned_dom["current_url"] = base_url
