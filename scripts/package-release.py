#!/usr/bin/env python3
"""Create source/skill ZIPs from tracked files; never bundle downloaded vehicle assets."""

import hashlib, json, subprocess, zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / "output/release"
out.mkdir(parents=True, exist_ok=True)
files = [
    Path(p)
    for p in subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    .decode()
    .split("\0")
    if p
]
blocked = (
    "public/models/",
    "public/templates/",
    "public/draco/",
    "node_modules/",
    "dist/",
    "assets/",
    "output/",
    ".venv/",
)
for p in files:
    if (
        str(p).startswith(blocked)
        or "local-checkout.json" in str(p)
        or ".runtime" in p.parts
    ):
        raise SystemExit(f"Refusing to package local/third-party runtime file: {p}")
if not files:
    raise SystemExit("Stage or commit the source files before packaging.")
source = out / "tesla-wrap-lab-source.zip"
skill = out / "tesla-wrap-lab-skill.zip"
with zipfile.ZipFile(source, "w", zipfile.ZIP_DEFLATED) as z:
    for p in files:
        z.write(root / p, Path("tesla-wrap-lab") / p)
with zipfile.ZipFile(skill, "w", zipfile.ZIP_DEFLATED) as z:
    for p in files:
        if p.parts[:2] == ("skills", "tesla-wrap-lab"):
            z.write(root / p, Path(*p.parts[1:]))
manifest = {
    p.name: {
        "bytes": p.stat().st_size,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
    }
    for p in [source, skill]
}
(out / "SHA256SUMS.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
