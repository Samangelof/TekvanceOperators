import sys
import asyncio
from robots.registry import REGISTRY


async def run_cli():
    if len(sys.argv) < 2:
        print("Укажи имя робота")
        return

    name = sys.argv[1]
    if name not in REGISTRY:
        print(f"Робот '{name}' не найден или повреждён.")
        return

    result = REGISTRY[name]()
    if asyncio.iscoroutine(result):
        await result


if __name__ == "__main__":
    asyncio.run(run_cli())
