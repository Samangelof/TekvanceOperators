class BaseRobot:
    def __init__(self, config: dict | None = None):
        self.config = config or {}

    def run(self):
        raise NotImplementedError("Реализуй run() в подклассе")
