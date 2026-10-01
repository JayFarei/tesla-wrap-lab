#!/usr/bin/env python3
"""Compose generated house emblems onto each model's separately measured layout."""

import json, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from wrap import ROOT, read_models, template_mask, export_image, register

HOUSES = [
    ("gryffindor", "Gryffindor", "#641c25", "#cda95c"),
    ("slytherin", "Slytherin", "#123d32", "#bfc4b4"),
    ("ravenclaw", "Ravenclaw", "#172c50", "#b28a58"),
    ("hufflepuff", "Hufflepuff", "#a77c25", "#282720"),
]


def place(canvas, image, box, angle=0):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    image = image.rotate(angle, expand=True)
    # Fit the complete generated emblem and fade only its plain background margins.
    image = ImageOps.contain(
        image, (int(w * 0.84), int(h * 0.86)), Image.Resampling.LANCZOS
    ).convert("RGBA")
    size = image.size
    alpha = Image.new("L", size)
    d = ImageDraw.Draw(alpha)
    pad = max(2, int(min(size) * 0.05))
    d.rounded_rectangle(
        (pad, pad, size[0] - pad - 1, size[1] - pad - 1), radius=pad, fill=255
    )
    alpha = alpha.filter(ImageFilter.GaussianBlur(pad))
    image.putalpha(alpha)
    canvas.alpha_composite(image, (x0 + (w - size[0]) // 2, y0 + (h - size[1]) // 2))


def compose(model, image, base, trim):
    canvas = Image.new("RGBA", (1024, 1024), base)
    d = ImageDraw.Draw(canvas)
    for key in ["leftDoor", "rightDoor", "leftRear", "rightRear"]:
        x0, y0, x1, y1 = model[key]
        d.rounded_rectangle(
            (x0 + 10, y0 + 10, x1 - 10, y1 - 10), radius=10, outline=trim, width=2
        )
    place(canvas, image, model["hood"])
    place(canvas, image, model["leftDoor"], -90)
    place(canvas, image, model["rightDoor"], 90)
    # No decoration bleeds onto windows: all islands use their exact model mask.
    return canvas


def main():
    for id, title, base, trim in HOUSES:
        image = Image.open(ROOT / "examples/artwork" / f"{id}.png")
        for model in read_models():
            canvas = compose(model, image, base, trim)
            with tempfile.TemporaryDirectory() as tmp:
                source = Path(tmp) / f"{id}-composed.png"
                canvas.save(source)
                dest, meta = export_image(
                    source, model["id"], title + ".png", base, True
                )
            register(
                id,
                title,
                model["id"],
                dest,
                "Hogwarts house · fan design",
                base,
                f"{title}-inspired heraldry, generated engraving and restrained house-colour panel trim. Unofficial fan artwork.",
            )
    source = (
        Image.open(ROOT / "examples/artwork/hogwarts-express-source.png")
        .convert("RGB")
        .resize((1024, 1024))
    )
    owl = source.crop((370, 180, 650, 505))
    for model in read_models():
        if model["id"] == "modely":
            path = ROOT / "examples/artwork/hogwarts-original-export.png"
            dest, meta = export_image(
                path, model["id"], "Hogwarts_Express.png", "#4c1119", True
            )
        else:
            canvas = compose(model, owl, "#4c1119", "#c9a25c")
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "express-adapted.png"
                canvas.save(path)
                dest, meta = export_image(
                    path, model["id"], "Hogwarts_Express.png", "#4c1119", True
                )
        register(
            "hogwarts",
            "Hogwarts Express",
            model["id"],
            dest,
            "Magical railway · fan design",
            "#641c25",
            "Burgundy and brass with generated owl heraldry. Original-body edition has carriage and map details; newer-body editions use a separately fitted emblem layout.",
        )
    for id, title, path, color in [
        ("f1", "F1 silver", "F1_Study_v2.png", "#aaaaaa"),
        ("alpine", "Alpine Expedition", "Expedition_AI.png", "#78958b"),
    ]:
        source = ROOT / "examples/artwork" / path
        if source.exists():
            dest, _ = export_image(source, "modely", path, color, True)
            register(
                id,
                title,
                "modely",
                dest,
                "Earlier study · original Model Y",
                color,
                "Earlier imagegen study, available only for the original Model Y template.",
            )
    print(
        "Model-specific examples built. Render and inspect before marking visual review complete."
    )


if __name__ == "__main__":
    raise SystemExit("Legacy emblem composer archived. Use scripts/build-rich-collection.py for the current full-body collection.")
