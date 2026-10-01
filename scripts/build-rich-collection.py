#!/usr/bin/env python3
"""Compose generated panel artwork onto separately segmented Model Y templates.

The recipes explicitly assign semantic parts, including split rear pieces; this is
not a resize of one finished vehicle atlas onto another model's mask.
"""

import argparse, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageOps
from wrap import ROOT, read_models, template_mask, export_image, register, digest

# Exact template connected components, sorted by their (top,left) bounds.
ORDER = {
    "modely": "wf bumper ef wr er hood ed wd em wm wb eb hatch wq eq rear".split(),
    "modely-2025-base": "bumper hood wf ef er wr wd ed em wm wb eb wq eq arch wx ex hatchlow".split(),
    "modely-2025-premium": "bumper hood wf ef wr wd er ed em wm wb eb wq eq wa ea hatchbar wx ex hatchlow".split(),
    "modely-2025-performance": "bumper hood wf ef wr er wd ed em wm wb eb wq eq wa ea hatchbar ex wx ws es hatchlow".split(),
    "modely-l": "wf ef bumper hood wr er wm em wd ed wb eb wa ea wq eq hatchbar wx ex hatchlow".split(),
}
# Source crops measured on generated panel sheets, in a normalized 1024px canvas.
CROPS = {
    "wf": (14, 7, 250, 272),
    "bumper": (245, 7, 780, 142),
    "ef": (774, 7, 1010, 272),
    "wr": (323, 130, 355, 630),
    "er": (667, 130, 697, 630),
    "hood": (354, 135, 675, 394),
    "wd": (20, 274, 203, 550),
    "ed": (822, 274, 1007, 550),
    "wm": (217, 396, 305, 460),
    "em": (719, 396, 805, 460),
    "wb": (20, 549, 224, 798),
    "eb": (797, 549, 1006, 798),
    "wq": (84, 789, 260, 950),
    "eq": (774, 789, 940, 950),
    "hatch": (298, 637, 727, 937),
    "rear": (240, 896, 779, 1014),
    "wa": (298, 638, 369, 779),
    "ea": (657, 638, 727, 779),
    "arch": (298, 638, 727, 820),
    "hatchbar": (341, 763, 686, 806),
    "hatchlow": (355, 799, 670, 937),
    "wx": (240, 896, 420, 1014),
    "ex": (600, 896, 779, 1014),
    "ws": (270, 950, 370, 1014),
    "es": (654, 950, 754, 1014),
}
THEMES = {
    "gryffindor": (
        "Gryffindor · Golden mane",
        "Gryffindor_Rich.png",
        "#4b0911",
        (357, 139, 672, 439),
    ),
    "slytherin": (
        "Slytherin · Silver serpent",
        "Slytherin_Rich.png",
        "#082e23",
        (357, 139, 674, 463),
    ),
    "hufflepuff": (
        "Hufflepuff · Golden harvest",
        "Hufflepuff_Rich.png",
        "#211b11",
        (354, 135, 675, 394),
    ),
    "hogwarts": (
        "Hogwarts Express · Night journey",
        "Hogwarts_Express_Rich.png",
        "#380a13",
        (354, 135, 675, 394),
    ),
    "ravenclaw": (
        "Ravenclaw · Celestial atelier",
        "Ravenclaw_Rich.png",
        "#10243c",
        (354, 135, 675, 394),
    ),
}


def components(model):
    remaining = template_mask(model)
    parts = []
    while remaining.getbbox():
        i = remaining.tobytes().index(255)
        before = remaining.copy()
        ImageDraw.floodfill(remaining, (i % 1024, i // 1024), 0)
        part = ImageChops.difference(before, remaining)
        if part.histogram()[255] > 100:
            parts.append(part)
    parts.sort(key=lambda p: (p.getbbox()[1], p.getbbox()[0]))
    if len(parts) != len(ORDER[model]):
        raise ValueError(f"Unexpected template topology for {model}")
    return dict(zip(ORDER[model], parts))


def compose(source, model, base, hood, theme):
    image = (
        Image.open(source).convert("RGB").resize((1024, 1024), Image.Resampling.LANCZOS)
    )
    atlas = Image.new("RGB", (1024, 1024), base)
    recipe = []
    for name, mask in components(model).items():
        box = mask.getbbox()
        crop = hood if name == "hood" else CROPS[name]
        entry = {
            "part": name,
            "sourceCrop": crop,
            "sourceSpace": "normalized 1024px atlas",
            "targetBounds": box,
        }
        artwork = image.crop(crop)
        if theme == "hogwarts" and name in ("wd", "ed", "wb", "eb"):
            mural = Image.open(
                ROOT / "examples/artwork/rich-collection/hogwarts-side-v2.png"
            ).convert("RGB")
            half = mural.width // 2
            mural_crop = (
                half if name.endswith("d") else 0,
                0,
                mural.width if name.endswith("d") else half,
                mural.height,
            )
            artwork = mural.crop(mural_crop)
            entry.update(
                sourceCrop=mural_crop,
                sourceSpace="hogwarts-side-v2.png native pixels",
                mirror=name.startswith("w"),
                rotateDegreesCCW=270 if name.startswith("w") else 90,
            )
            # Roof-facing edge is inward; forward direction is atlas north on both sides.
            artwork = (
                ImageOps.mirror(artwork).transpose(Image.Transpose.ROTATE_270)
                if name.startswith("w")
                else artwork.transpose(Image.Transpose.ROTATE_90)
            )
        elif theme == "hogwarts" and name in ("wq", "eq"):
            entry.update(
                mirror=name.startswith("w"),
                rotateDegreesCCW=270 if name.startswith("w") else 90,
            )
            artwork = (
                ImageOps.mirror(artwork).transpose(Image.Transpose.ROTATE_270)
                if name.startswith("w")
                else artwork.transpose(Image.Transpose.ROTATE_90)
            )
        artwork = artwork.resize(
            (box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS
        )
        atlas.paste(artwork, box, mask.crop(box))
        recipe.append(entry)
    return atlas, recipe


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--theme", choices=list(THEMES))
    p.add_argument("--model", choices=list(ORDER))
    p.add_argument("--replace", action="store_true")
    a = p.parse_args()
    for theme, (title, name, base, hood) in THEMES.items():
        if a.theme and a.theme != theme:
            continue
        source = ROOT / "examples/artwork/rich-collection" / f"{theme}-v1.png"
        if theme == "ravenclaw":
            source = ROOT / "public/studies/ravenclaw/atlas-C-clean.png"
        for m in read_models():
            model = m["id"]
            if a.model and a.model != model:
                continue
            canvas, recipe = compose(source, model, base, hood, theme)
            actual_source = source
            if theme == "ravenclaw" and model == "modely":
                actual_source = ROOT / "public/studies/ravenclaw/atlas-C-registered.png"
                canvas = Image.open(actual_source)
                recipe = [
                    {
                        "method": "Existing mesh-anchored original-body hybrid retained unchanged"
                    }
                ]
            work = ROOT / "artifacts/rich-collection" / theme / model
            work.mkdir(parents=True, exist_ok=True)
            path = work / "composed.png"
            canvas.save(path)
            dest, meta = export_image(path, model, name, base, a.replace)
            meta["composition"] = {
                "method": "Semantic panel crops resampled to this exact model’s template components",
                "artworkSha256": digest(actual_source),
                "artworkFile": str(actual_source.relative_to(ROOT)),
                "recipe": recipe,
            }
            if theme == "hogwarts":
                meta["composition"]["sideMuralSha256"] = digest(
                    ROOT / "examples/artwork/rich-collection/hogwarts-side-v2.png"
                )
            dest.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")
            register(
                theme,
                title,
                model,
                dest,
                "Hogwarts collection · full-body",
                base,
                "Detailed generated engraving composed separately for each body: hood, doors, fenders, mirrors, painted roof rails and rear pieces. Unofficial fan artwork; inspect final appearance in-car.",
            )
    print(
        "Composed rich collection. Render each model and inspect before updating review status."
    )


if __name__ == "__main__":
    main()
