"""
Sobe o servidor Django na porta configurada em HOST_PORT (.env).
"""

import os
import subprocess
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
os.chdir(_root)

from dotenv import load_dotenv

load_dotenv(_root / ".env")
port = os.getenv("HOST_PORT", "3000")

sys.exit(subprocess.call([sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}"]))
