# Rich Hogwarts collection

The current five themes use full-body generated engraving rather than a small crest on plain paint. Original generated sheets and exact prompts are retained here; Ravenclaw reuses `public/studies/ravenclaw/atlas-C-clean.png`, with the registered original-body version retained for `modely`.

## Composition

`python3 scripts/build-rich-collection.py --replace` deliberately rebuilds the existing collection. Omit `--replace` to protect existing outputs. `--theme` and `--model` restrict the build. The old `build-examples.py` entry point is disabled so it cannot accidentally restore the simpler catalogue.

Each target template is independently segmented into its paint islands. A checked, model-specific part order maps generated hood, front/rear doors, fenders, mirrors, roof rails and rear pieces to that body's islands. The rear panel topology differs between models; it has explicit split-piece recipes. PNG sidecars record source hashes, source crops, rotations and target bounds. This is a reproducible manual composition recipe, not an automatic UV correspondence solver. It does not establish pixel-perfect seam continuity or exact feature registration across all models.

## Screenshot-guided Express correction

The first mapped Express render (`hogwarts-before-left.png`) revealed sideways trains and viaduct arches on the rotated door islands. Imagegen received the actual render and original source, then produced the independent, upright `hogwarts-side-v2.png` mural using `correction-prompt.txt`. The composer splits that mural across front/rear doors, rotates each side into its UV orientation and mirrors the opposite side so the locomotive faces forward. Quarter-panel scenery is also rotated upright. The top of the mural leaves quieter space around the actual door handles.

Five-angle contact sheets were inspected for all 25 current collection exports. The trains now read upright on both sides; hood motifs, side engraving and rear treatments appear on their intended surfaces. The four house compositions showed no comparably severe orientation error, so no additional imagegen correction was made for them. They use broad engraving rather than precision ornament frames around every handle. The original Ravenclaw keeps its earlier mesh-anchored ornaments; the other bodies do not claim that registration.

Remaining limitations: some graphics break or change scale at door/fender and rear-panel seams; the Express mural has a small discontinuity at the door split; fine linework is compressed to Tesla's 1024px/1MB limit. Black glass, wheels and reflections come from the preview mesh/materials. These are reviewed local previews, not verified in-car results.

## Car-only presentation

Run `PLAYWRIGHT_CHANNEL=chrome npm run review -- --all --out examples/reviews` for raw, UI-free WebGL captures (omit the environment variable when using Playwright's installed Chromium). Then run `python3 scripts/build-showcase.py`. It validates capture hashes, crops background margins and adds consistent padding; it never repaints, relights or retouches the car. The result is a responsive collection at `/gallery/index.html`, plus README screenshots. Add `?model=modely` to show only original-body cars. Select any car to open the interactive viewer.
