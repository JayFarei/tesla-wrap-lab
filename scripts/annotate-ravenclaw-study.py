"""Visualize the study's manual annotations; this does not discover feature centres."""

import json
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1] / "public/studies/ravenclaw"
data = json.loads((root / "measurement.json").read_text())
out = Image.new("RGB", (1000, 795), "#f4f1ea")
draw = ImageDraw.Draw(out)
variants = [
    ("A concept-first", "review-A-v1/modely-raven-concept-v1-left.png"),
    ("B template-first", "review-B-v1/modely-raven-template-v1-left.png"),
    ("C hybrid", "review-C-v3/modely-raven-celestial-v3-left.png"),
]
for i, (name, file) in enumerate(variants):
    image = Image.open(root / file).convert("RGB")
    marks = ImageDraw.Draw(image)
    row = next(r for r in data["results"] if r["approach"] == name)
    for x, y in data["referenceCentres"].values():
        marks.line((x - 4, y, x + 4, y), fill="#00ff30", width=1)
        marks.line((x, y - 4, x, y + 4), fill="#00ff30", width=1)
    for x, y in row["ornamentCentres"].values():
        marks.ellipse((x - 3, y - 3, x + 3, y + 3), outline="#ff3344", width=1)
    image = image.crop((255, 325, 560, 400)).resize((915, 225))
    out.paste(image, (20, i * 265 + 28))
    draw.text(
        (20, i * 265 + 8),
        f"{name}: {row['meanOffsetPixels']}px approximate mean offset. Green: reference handle centre; red: ornament centre.",
        fill="black",
    )
out.save(root / "alignment-check.png")
