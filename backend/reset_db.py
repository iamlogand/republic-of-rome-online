"""
Wipes the database, runs all migrations, and creates a superuser.

Usage: python reset_db.py
Superuser credentials after reset: admin / password
"""

import os
import subprocess
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

for candidate in [
    os.path.join(script_dir, ".venv", "Scripts", "python.exe"),  # Windows
    os.path.join(script_dir, ".venv", "bin", "python"),  # Unix/Mac
]:
    if os.path.exists(candidate):
        python = candidate
        break
else:
    python = sys.executable

subprocess.run([python, "manage.py", "reset_db", "--noinput"], check=True)
subprocess.run([python, "manage.py", "migrate"], check=True)
subprocess.run(
    [
        python,
        "manage.py",
        "createsuperuser",
        "--noinput",
        "--username",
        "admin",
        "--email",
        "admin@example.com",
    ],
    env={**os.environ, "DJANGO_SUPERUSER_PASSWORD": "password"},
    check=True,
)

print("\nDone")
