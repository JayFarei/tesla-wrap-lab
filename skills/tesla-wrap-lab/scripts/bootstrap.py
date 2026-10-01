#!/usr/bin/env python3
"""Resolve or clone the viewer; optionally install dependencies into that checkout."""

import argparse, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/jayfarei/tesla-wrap-lab.git"


def valid(p):
    return (p / "public/models.json").is_file() and (p / "scripts/wrap.py").is_file()


def resolve():
    specified = os.environ.get("TESLA_WRAP_LAB_DIR")
    if specified:
        p = Path(specified).expanduser().resolve()
        if not valid(p):
            raise RuntimeError("TESLA_WRAP_LAB_DIR does not point to Tesla Wrap Lab")
        return p
    config = SKILL / "local-checkout.json"
    if config.exists():
        p = Path(json.loads(config.read_text())["path"])
        if valid(p):
            return p
    for parent in SKILL.parents:
        if valid(parent):
            return parent
    p = SKILL / ".runtime/tesla-wrap-lab"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", REPO_URL, str(p)], check=True)
    if not valid(p):
        raise RuntimeError(
            f"Incomplete checkout at {p}; choose a valid TESLA_WRAP_LAB_DIR"
        )
    return p


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup", action="store_true")
    args = parser.parse_args()
    root = resolve()
    python = (
        root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    if args.setup:
        if not shutil.which("npm"):
            raise RuntimeError("Install Node.js 20+ and npm, then retry.")
        lock = hashlib.sha256((root / "package-lock.json").read_bytes()).hexdigest()
        stamp = root / "node_modules/.wrap-lab-lock.sha256"
        if not stamp.exists() or stamp.read_text() != lock:
            subprocess.run(["npm", "ci"], cwd=root, check=True)
            stamp.write_text(lock)
        subprocess.run(["npm", "run", "setup:assets"], cwd=root, check=True)
        if not python.exists():
            subprocess.run(
                [sys.executable, "-m", "venv", str(root / ".venv")], check=True
            )
        subprocess.run(
            [str(python), "-m", "pip", "install", "-r", str(root / "requirements.txt")],
            check=True,
        )
    print(
        json.dumps(
            {
                "checkout": str(root),
                "python": str(python),
                "start": "npm run dev -- --port 5178",
                "cwd": str(root),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as e:
        sys.exit(str(e))
