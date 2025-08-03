import json
from  robots.robot_knp.brain import KnpRobot


CONFIG_PATH = "robots/robot_knp/config.json"

if __name__ == "__main__":
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    bot = KnpRobot(config=config)
    try:
        bot.run()
    finally:
        bot.close()
