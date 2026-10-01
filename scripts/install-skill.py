#!/usr/bin/env python3
"""Install a linked local skill without overwriting an unrelated installation."""

import argparse, json, os, shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--destination", type=Path)
p.add_argument("--replace", action="store_true")
args = p.parse_args()
dest = (
    args.destination
    or Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    / "skills/tesla-wrap-lab"
)
if dest.exists() and not args.replace:
    p.error(f"{dest} exists; use --replace to explicitly update it")
dest.mkdir(parents=True, exist_ok=True)
shutil.copytree(
    root / "skills/tesla-wrap-lab",
    dest,
    dirs_exist_ok=True,
    ignore=shutil.ignore_patterns(".runtime", "local-checkout.json", "__pycache__"),
)
(dest / "local-checkout.json").write_text(
    json.dumps({"path": str(root)}, indent=2) + "\n"
)
print(
    f"Installed {dest}. Start a new Codex session if it is not discovered immediately."
)
