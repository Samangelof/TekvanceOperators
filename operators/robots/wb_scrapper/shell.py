# robots/wb_scrapper/shell.py
from robots.wb_scrapper.brain import WbRobot


def run(config=None):
    bot = WbRobot(config=config or {})
    try:
        bot.run()
    finally:
        bot.close()
