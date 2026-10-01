#!/usr/bin/env python3
"""Model-bound PNG export, catalogue registration and deterministic validation."""

import argparse, hashlib, io, json, re, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 1_000_000


def read_models():
    return json.loads((ROOT / "public/models.json").read_text())


def model_by_id(id):
    for m in read_models():
        if m["id"] == id:
            return m
    raise ValueError(f"Unknown Model Y template: {id}")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def valid_name(name):
    if not re.fullmatch(r"[A-Za-z0-9_ -]{1,26}\.png", name):
        raise ValueError(
            "Use a .png filename with 1–26 alphanumeric, space, dash or underscore characters before .png."
        )


def validate(path):
    path = Path(path)
    valid_name(path.name)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f"{path}: over 1 MB")
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError(f"{path}: not PNG")
        if image.width != image.height or not 512 <= image.width <= 1024:
            raise ValueError(f"{path}: expected square 512–1024px PNG")
        image.verify()
    return {"file": str(path), "bytes": path.stat().st_size, "sha256": digest(path)}


def template_mask(model):
    path = ROOT / "public/templates" / f"{model}.png"
    mask = (
        Image.open(path)
        .convert("L")
        .resize((1024, 1024))
        .point(lambda p: 255 if p > 220 else 0)
    )
    # Only discard white exterior page margins connected to image boundaries.
    for x in range(1024):
        for y in (0, 1023):
            if mask.getpixel((x, y)):
                ImageDraw.floodfill(mask, (x, y), 0)
    for y in range(1024):
        for x in (0, 1023):
            if mask.getpixel((x, y)):
                ImageDraw.floodfill(mask, (x, y), 0)
    return mask


def export_image(source, model, name, base="#777777", replace=False):
    model_by_id(model)
    valid_name(name)
    source = Path(source).resolve()
    dest = ROOT / "public/wraps" / model / name
    if dest.exists() and not replace:
        raise ValueError(
            f"{dest} exists; choose a new version name or explicitly use --replace"
        )
    with Image.open(source) as original:
        if original.width != original.height:
            raise ValueError(
                "The fitted atlas must be square; compose rectangular artwork onto a square canvas first to avoid distortion."
            )
        artwork = original.convert("RGBA").resize(
            (1024, 1024), Image.Resampling.LANCZOS
        )
    backing = Image.new("RGBA", (1024, 1024), base)
    backing.alpha_composite(artwork)
    out = Image.new("RGB", (1024, 1024), base)
    out.paste(backing.convert("RGB"), (0, 0), template_mask(model))
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Preserve full colour whenever it fits. Quantization is a size fallback.
    encoded = io.BytesIO()
    out.save(encoded, format="PNG", optimize=True)
    encoding = "RGB"
    if encoded.tell() > MAX_BYTES:
        encoded = io.BytesIO()
        out.quantize(colors=256, method=Image.Quantize.MEDIANCUT).save(
            encoded, format="PNG", optimize=True
        )
        encoding = "indexed-256"
    if encoded.tell() > MAX_BYTES:
        raise ValueError(
            "Encoded PNG still exceeds 1 MB; simplify fine noise in the source."
        )
    # Validate before replacing an existing good export.
    with tempfile.TemporaryDirectory(dir=dest.parent) as staging:
        candidate = Path(staging) / name
        candidate.write_bytes(encoded.getvalue())
        validate(candidate)
        candidate.replace(dest)
    info = validate(dest)
    meta = {
        "encoding": encoding,
        "model": model,
        "templateSha256": digest(ROOT / "public/templates" / f"{model}.png"),
        "sourceSha256": digest(source),
        "sha256": info["sha256"],
        "bytes": info["bytes"],
        "inCarVerified": False,
        "visualReview": "not reviewed",
        "sourceFile": source.name,
    }
    dest.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")
    return dest, meta


def register(
    id,
    title,
    model,
    path,
    category="Custom",
    color="#78958b",
    description="Custom generated artwork.",
):
    if not re.fullmatch("[a-z0-9-]+", id):
        raise ValueError("id must be lowercase letters, digits and dashes")
    file = ROOT / "public/catalog.json"
    items = json.loads(file.read_text()) if file.exists() else []
    row = next((r for r in items if r["id"] == id), None)
    if not row:
        row = dict(
            id=id,
            name=title,
            category=category,
            color=color,
            description=description,
            models={},
        )
        items.append(row)
    relative = Path(path).resolve().relative_to((ROOT / "public").resolve())
    row["models"][model] = {
        "file": "/" + relative.as_posix(),
        "filename": Path(path).name,
        "status": "Generated candidate · alignment and in-car appearance unverified.",
    }
    file.write_text(json.dumps(items, indent=2) + "\n")


def validate_catalog():
    ids = set()
    count = 0
    for row in json.loads((ROOT / "public/catalog.json").read_text()):
        if row["id"] in ids:
            raise ValueError("Duplicate catalogue id")
        ids.add(row["id"])
        for model, entry in row["models"].items():
            model_by_id(model)
            p = (ROOT / "public" / entry["file"].lstrip("/")).resolve()
            if not p.is_relative_to((ROOT / "public/wraps" / model).resolve()):
                raise ValueError("Wrap path does not match model")
            info = validate(p)
            meta = json.loads(p.with_suffix(".json").read_text())
            if meta.get("bytes") != info["bytes"]:
                raise ValueError("PNG byte count mismatch")
            if meta["model"] != model or meta["sha256"] != info["sha256"]:
                raise ValueError("Model or PNG checksum mismatch")
            if meta["templateSha256"] != digest(
                ROOT / "public/templates" / f"{model}.png"
            ):
                raise ValueError("Template checksum changed")
            if entry["filename"] != p.name:
                raise ValueError("Download filename mismatch")
            count += 1
    print(
        f"Validated {count} model-bound PNGs across {len(ids)} designs. This does not verify visual fit or in-car acceptance."
    )


def validate_review(file):
    file = Path(file).resolve()
    report = json.loads(file.read_text())
    if report.get("errors"):
        raise ValueError("Capture report contains browser errors")
    rows = json.loads((ROOT / "public/catalog.json").read_text())
    if not report.get("records"):
        raise ValueError("Capture report has no records")
    for record in report["records"]:
        row = next((r for r in rows if r["id"] == record["wrap"]), None)
        if not row or record["model"] not in row["models"]:
            raise ValueError("Capture target no longer exists")
        entry = row["models"][record["model"]]
        if record.get("pngFile") != entry["file"]:
            raise ValueError("Capture PNG path does not match catalogue")
        png = (ROOT / "public" / entry["file"].lstrip("/")).resolve()
        if not png.is_relative_to((ROOT / "public/wraps" / record["model"]).resolve()):
            raise ValueError("Capture model path mismatch")
        if digest(png) != record["pngSha256"]:
            raise ValueError("Stale capture: PNG has changed; render again")
        if set(record["views"]) != {"front", "rear", "left", "right", "top"}:
            raise ValueError("Capture needs all five views")
        for view in record["views"].values():
            image = (file.parent / view["file"]).resolve()
            if not image.is_relative_to(file.parent) or digest(image) != view["sha256"]:
                raise ValueError("Screenshot checksum/path mismatch")
    print(
        f"Validated evidence binding for {len(report['records'])} exports. This does not approve visual fit."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("models")
    sub.add_parser("validate-catalog")
    v = sub.add_parser("validate")
    v.add_argument("file")
    r = sub.add_parser("validate-review")
    r.add_argument("file")
    e = sub.add_parser("export")
    e.add_argument("--model", required=True)
    e.add_argument("--source", required=True)
    e.add_argument("--name", required=True)
    e.add_argument("--base", default="#777777")
    e.add_argument("--replace", action="store_true")
    e.add_argument("--id")
    e.add_argument("--title")
    args = parser.parse_args()
    try:
        if args.command == "models":
            print(json.dumps(read_models(), indent=2))
        elif args.command == "validate":
            print(json.dumps(validate(args.file), indent=2))
        elif args.command == "validate-catalog":
            validate_catalog()
        elif args.command == "validate-review":
            validate_review(args.file)
        elif args.command == "export":
            if bool(args.id) != bool(args.title):
                raise ValueError("Supply both --id and --title to register a design")
            if args.id and not re.fullmatch("[a-z0-9-]+", args.id):
                raise ValueError("id must be lowercase letters, digits and dashes")
            dest, meta = export_image(
                args.source, args.model, args.name, args.base, args.replace
            )
            if args.id:
                register(args.id, args.title, args.model, dest)
            print(json.dumps({"file": str(dest), **meta}, indent=2))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
