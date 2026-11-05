import py_compile
from pathlib import Path


def test_launcher_and_app_compile():
    root = Path(__file__).resolve().parent.parent
    for f in ("launcher.py", "app.py"):
        py_compile.compile(str(root / f), doraise=True)
