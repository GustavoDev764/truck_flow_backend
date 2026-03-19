"""
Formata todo o projeto Python com Black e Ruff.
- Black: formatação de código (padrão de mercado)
- Ruff: ordenação de imports (isort), validação, remove código comentado (ERA)
- Remove comentários (#) do código (preserva docstrings)
"""

import subprocess
import sys
import tokenize
from io import StringIO
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", ".venv", "__pycache__", "migrations", "htmlcov", "node_modules"}


def remove_comments(filepath: Path) -> bool:
    """Remove comentários # do arquivo (preserva docstrings)."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tokens = [
            tok
            for tok in tokenize.generate_tokens(StringIO(source).readline)
            if tok.type != tokenize.COMMENT
        ]
        new_source = tokenize.untokenize(tokens)
        if new_source != source:
            filepath.write_text(new_source, encoding="utf-8")
            return True
    except (tokenize.TokenError, SyntaxError, OSError):
        pass
    return False


def main() -> int:
    py_files = [
        p for p in BACKEND_ROOT.rglob("*.py") if not any(ex in p.parts for ex in EXCLUDE_DIRS)
    ]

    print("Removendo comentários (#)...")
    removed = sum(1 for p in py_files if remove_comments(p))
    if removed:
        print(f"  {removed} arquivo(s) alterado(s)")

    print("Executando Ruff (lint + fix + ordenar imports)...")
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--fix", str(BACKEND_ROOT)],
        cwd=str(BACKEND_ROOT),
    )
    if r.returncode != 0:
        print("Ruff: alguns erros podem precisar de correção manual.")

    print("Executando Black (formatação)...")
    r = subprocess.run(
        [sys.executable, "-m", "black", str(BACKEND_ROOT)],
        cwd=str(BACKEND_ROOT),
    )
    if r.returncode != 0:
        return r.returncode

    print("Formatação concluída com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
