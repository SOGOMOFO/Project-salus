import ast
from pathlib import Path


def is_valid_python_file(path: Path) -> bool:
    if not path.exists():
        return False

    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return False

    return True
