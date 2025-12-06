import asyncio
import random

from oxymouse import OxyMouse
from playwright.async_api import Page


class MouseMovements:
    """
    Class to handle random mouse movements in pyba

    These functions need to be happening async to actions such as waiting for page to load. This class
    will replace all `time.sleep()`, `asyncio.sleep()` and `wait_for_*` functionality.

    The movements are deliberately constrained to a specific region in the viewport.

    For more information on the algorithms, check out https://github.com/oxylabs/OxyMouse
    """

    def __init__(self, page: Page, width: int = 1200, height: int = 1024):
        """
        Args:
            `page`: The current page object
            `width`: The viewport width for the session, defaults at 1200
            `height`: The viewport height for the session, defaults at 1024
        """
        print("calling mouse")
        self.page = page

        # Picks a random number between 0 and the viewport values with mode as 500
        self.width = int(random.triangular(0, width, 600))
        self.height = int(random.triangular(0, height, 512))

    async def _run(self, algorithm: str):
        """
        Runs the mouse movements for a specified algorithm

        (NOTE: This is constrained to a small window)
        """
        mouse = OxyMouse(algorithm=algorithm)
        movements = mouse.generate_random_coordinates(
            viewport_width=self.width,
            viewport_height=self.height,
        )

        for x, y in movements:
            await self.page.mouse.move(int(x), int(y), steps=10)
            await asyncio.sleep(random.uniform(0.004, 0.015))

    async def bezier_movements(self):
        """
        Function to perform bezier curve movements
        """
        await self._run(algorithm="bezier")

    async def gaussian_movements(self):
        """
        Function to perform gaussian movements
        """
        await self._run(algorithm="gaussian")

    async def perlin_movements(self):
        """
        Function to perform perlin movements
        """
        await self._run(algorithm="perlin")

    async def random_movement(self):
        """
        Chooses a function at random
        """

        mapping = {
            1: self.bezier_movements,
            2: self.gaussian_movements,
            3: self.perlin_movements,
        }

        _ = mapping[random.randint(1, 3)]
        await _()
