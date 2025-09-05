# robots/robot_knp/shell.py
from robots.robot_knp.brain import KnpController


def run(config=None):
    bot = KnpController(config=config or {})
    try:
        bot.run()
    finally:
        bot.close()
