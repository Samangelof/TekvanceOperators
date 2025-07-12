# robots/robot_knp/shell.py
from robots.robot_knp.brain import KnpRobot


def run(config=None):
    bot = KnpRobot(config=config or {})
    try:
        bot.run()
    finally:
        bot.close()
