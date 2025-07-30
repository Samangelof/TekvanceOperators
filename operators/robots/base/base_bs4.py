import httpx
from bs4 import BeautifulSoup
from robots.base.base import BaseRobot


class BaseBSRobot(BaseRobot):
    def get_soup(self, url):
        resp = httpx.get(url)
        return BeautifulSoup(resp.text, "html.parser")
