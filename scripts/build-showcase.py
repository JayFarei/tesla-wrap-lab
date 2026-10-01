#!/usr/bin/env python3
"""Crop verified raw WebGL captures into car-only showcase assets (no retouching)."""

import json
from pathlib import Path
from PIL import Image, ImageChops, ImageOps

ROOT = Path(__file__).resolve().parents[1]
THEMES = ["hogwarts", "gryffindor", "slytherin", "ravenclaw", "hufflepuff"]
MODELS = [
    "modely",
    "modely-2025-base",
    "modely-2025-premium",
    "modely-2025-performance",
    "modely-l",
]


def tile(source, size=(1000, 600)):
    image = Image.open(source).convert("RGB")
    background = image.getpixel((0, 0))
    delta = ImageChops.difference(
        image, Image.new("RGB", image.size, background)
    ).convert("L")
    bounds = delta.point(lambda p: 255 if p > 12 else 0).getbbox()
    if not bounds:
        raise ValueError(f"Empty capture: {source}")
    car = ImageOps.contain(
        image.crop(bounds),
        (int(size[0] * 0.90), int(size[1] * 0.88)),
        Image.Resampling.LANCZOS,
    )
    result = Image.new("RGB", size, background)
    result.paste(car, ((size[0] - car.width) // 2, (size[1] - car.height) // 2))
    return result


def main():
    from wrap import validate_review

    capture = ROOT / "examples/reviews/capture.json"
    validate_review(capture)
    report = json.loads(capture.read_text())
    dest = ROOT / "public/gallery/cars"
    dest.mkdir(parents=True, exist_ok=True)
    for record in report["records"]:
        for view in record["views"].values():
            tile(capture.parent / view["file"]).save(
                dest / Path(view["file"]).with_suffix(".webp"), quality=92
            )

    def car(model, theme, angle="front"):
        return tile(capture.parent / f"{model}-{theme}-{angle}.png")

    docs = ROOT / "docs/screenshots"
    car("modely", "hogwarts").save(docs / "studio.png")
    car("modely", "ravenclaw").save(docs / "ravenclaw.png")
    car("modely", "hogwarts", "rear").save(docs / "mobile.png")
    for filename, rows, cols, themes, models in [
        ("collection.png", 2, 2, THEMES[1:], ["modely"]),
        ("model-matrix.png", 5, 5, THEMES, MODELS),
        (
            "ravenclaw-comparison.png",
            1,
            3,
            ["raven-concept-v1", "raven-template-v1", "raven-celestial-v3"],
            ["modely"],
        ),
    ]:
        cell = (700, 420)
        sheet = Image.new("RGB", (cols * cell[0], rows * cell[1]), (233, 236, 229))
        for i, (theme, model) in enumerate((t, m) for t in themes for m in models):
            shot = car(model, theme).resize(cell, Image.Resampling.LANCZOS)
            sheet.paste(shot, ((i % cols) * cell[0], (i // cols) * cell[1]))
        sheet.save(docs / filename)
    catalog = json.loads((ROOT / "public/catalog.json").read_text())
    entries = []
    for row in catalog:
        for model in row["models"]:
            entries.append(
                {
                    "model": model,
                    "wrap": row["id"],
                    "name": row["name"],
                    "image": f'cars/{model}-{row["id"]}-front.webp',
                }
            )
    (dest.parent / "cars.json").write_text(json.dumps(entries, indent=2) + "\n")
    print(f"Built {len(entries)} car-only previews and README images.")


if __name__ == "__main__":
    main()
