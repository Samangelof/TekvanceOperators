from playwright.async_api import async_playwright
from robots.base.base import BaseRobot


class BasePlaywrightRobot(BaseRobot):
    async def init_browser(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=True)
        self.page = await self.browser.new_page()

    async def close(self):
        await self.browser.close()
        await self.pw.stop()
