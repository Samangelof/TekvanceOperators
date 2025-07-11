def run_cli():
    from robots.registry import REGISTRY
    import sys

    if len(sys.argv) < 2:
        print("Укажи имя робота")
        return

    name = sys.argv[1]
    if name not in REGISTRY:
        print(f"Робот '{name}' не найден или повреждён.")
        return

    REGISTRY[name]()
