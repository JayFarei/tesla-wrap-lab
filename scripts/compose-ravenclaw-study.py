from pathlib import Path
import json
from PIL import Image

root = Path(__file__).resolve().parents[1] / "public/studies/ravenclaw"
source = Image.open(root / "atlas-A-v2.png").convert("RGBA")
patch = source.crop((156, 542, 224, 656))
# Extract generated ink and the inset, not surrounding feather fragments.
pixels = patch.load()
for y in range(patch.height):
    for x in range(patch.width):
        r, g, b, a = pixels[x, y]
        inside = ((x - 34) / 22.5) ** 2 + ((y - 56) / 44.5) ** 2 <= 1
        generated_gold = r > g * 1.04 and g > b * 1.1 and r > 85
        pixels[x, y] = (r, g, b, 255 if inside or generated_gold else 0)
patch = patch.resize((38, 66), Image.Resampling.LANCZOS)
patch.save(root / "generated-handle-ornament.png")
atlas = (
    Image.open(root / "atlas-C-clean.png")
    .convert("RGBA")
    .resize((1024, 1024), Image.Resampling.LANCZOS)
)
anchors = {
    "rightFront": [173, 492],
    "rightRear": [177, 712],
    "leftFront": [851, 492],
    "leftRear": [847, 712],
}
for x, y in anchors.values():
    atlas.alpha_composite(
        patch, (round(x - patch.width / 2), round(y - patch.height / 2))
    )
atlas.convert("RGB").save(root / "atlas-C-registered.png")
(root / "anchors.json").write_text(
    json.dumps(
        {
            "model": "modely",
            "uvChannel": 1,
            "canvas": [1024, 1024],
            "anchors": anchors,
            "method": "Nearest painted surface raycast at visually located handles. Screen probes retained in probes.json; approximate landmark centres, not CAD-defined hardware centres.",
            "ornamentSize": [38, 66],
        },
        indent=2,
    )
    + "\n"
)
