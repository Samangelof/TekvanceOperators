import sys

if __name__ == "__main__":
    if "--cli" in sys.argv:
        from cli import run_cli
        run_cli()
    else:
        from gui.main import run_gui
        run_gui()