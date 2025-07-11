from robots.registry import REGISTRY

def run_robot(name, config):
    REGISTRY[name](config)
