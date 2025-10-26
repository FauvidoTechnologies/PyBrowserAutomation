from playwright.async_api import Page

from pyba.utils.load_yaml import load_config


class YouTubeDOMExtraction:
    """
    Extracts links along with their texts from a youtube page. This is specifically designed for youtube pages, and can be used
    either when a search result is queried and videos are being browsed or when a video is playing and something else needs to
    be clicked.

    This provides an exhaustive list of the valid selectors and buttons which are needed for interacting on YouTube.
    """

    def __init__(self, page: Page):
        """
        Evaluates javascript inside the browser page

        1. links on the page along with their titles (for all visible videos)
        2. input fields for searches and comments
        3. Buttons for like and dislike etc.
        """
        self.page = page
        self.config = load_config("extraction")["youtube"]

    async def extract_links_and_titles(self):
        """
        Extracts all the video links and their title names from a YouTube page. Its simply checking for
        all possible `/watch?v=` type selectors and querying their names. We're first writing the vanilla
        Javascript which is to be executed in the browser session to get all the results from it, otherwise
        we'd need to use BeautifulSoup.
        """

        js_code = """
            (config) => {
                const anchors = Array.from(document.querySelectorAll(config.link_selector));
                const results = [];

                for (const a of anchors) {
                    let titleEl = null;

                    titleEl = a.querySelector(config.title_selector);

                    let title =
                        titleEl?.textContent?.trim() ||
                        a.getAttribute(config.usual_title_name) ||        // The second fallback from titleEl
                        a.getAttribute(config.label_name) ||     // The third fallback
                        "";

                    if (title && a.href && a.getAttribute('href').startsWith(config.usual_youtube_relative_link_format)) {
                        results.push({
                            title,
                            href: new URL(a.getAttribute('href'), window.location.origin).href
                        });
                    }
                }

                // Removing duplicates
                const seen = new Set();
                return results.filter(v => {
                    if (seen.has(v.href)) return false;
                    seen.add(v.href);
                    return true;
                });
            }
        """

        # TODO: As a fallback mechanism we can also use bs4 in here
        videos = await self.page.evaluate(js_code, self.config)

        # We don't want to touch the page again or any other system
        return videos
