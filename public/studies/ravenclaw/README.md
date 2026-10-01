# Ravenclaw: body-aware design experiment

Target: original/pre-2025 Model Y (`modely`). Built-in imagegen supplied every new raster illustration. Code performed composition, cropping, resampling, alpha extraction and exact placement. No generated concept is presented as a real wrap render.

## Approaches and evidence

| Approach | Inputs and conversion | Finding |
|---|---|---|
| A: concept-first | Five neutral mesh views → multi-view concept → exact template and a feature guide → atlas | Rich, coherent feather sweep. Generated handle surrounds were offset and panel outlines introduced dark bands. |
| B: template-first | Exact template, feature guide and neutral views → atlas directly | Attractive bold forms but more segmented door composition. Handle placement still guessed. |
| C: hybrid | A → actual viewer screenshots → corrected atlas → imagegen removes embedded handle ornaments → code places an extracted generated ornament at measured anchors | Best feature alignment in this trial; rich body-wide artwork survives. Still not perfectly seamless. |

The first correction (`atlas-A-v2.png`) removed fake black handle slots but did not reliably move ornaments to the requested coordinates. The second correction removed all four ornaments, giving `atlas-C-clean.png`. `scripts/compose-ravenclaw-study.py` cuts generated ink from the v2 source and places it at the four model-specific anchors; it does not draw substitute artwork. This produces `atlas-C-registered.png`, then the ordinary exporter produces `Raven_Celestial_v3.png`.

Five views were captured for all four exports, including the intermediate v2. Front/side views guided the choice and corrections; the final hybrid was inspected individually from all five angles. No in-car check occurred. Each capture JSON binds screenshots to the exact export hash and can be checked with `scripts/wrap.py validate-review <capture.json>`.

## What was measured

`measurement.json` records manually annotated ornament centres in fixed 994 × 740 left-side images. Mean distance from the neutral car's two visible handle centres is approximately A 14px, B 20px and C 3px, with about ±3px reading uncertainty. These are screen-space diagnostics, not physical millimetres, CAD-derived centres or an independent statistical evaluation. Only one primary output was sampled per approach; C also received extra refinement, so this cannot establish a universal ranking of generation methods.

The centre readings are reproducible by opening the left-view PNGs and the neutral reference at native size. `probes.json` records actual second-UV raycast samples around the visually identified features. `anchors.json` holds the approximate selected anchor centres, not an assertion that the GLB explicitly labels its handles. The mesh confirms which surface receives the pixels; the human/agent supplies semantic labels.

## Remaining defects

There are dark bands at some door/fender boundaries, imperfect feather continuation between separate islands, cropped fine cartography, and ornate roof-rail dots that the first correction did not remove. The side ornaments align much better but retain printed shading. Lower rear surfaces and glass/wheels cannot be repainted by this texture. The design is much richer than the crest study, but it does not exactly reproduce every detail of the concept.

The current files belong only to the original Model Y. Other bodies need new references, anchors, fitting and review; copying this atlas or these coordinates would not be sufficient.

## Reproduce

1. Set up repository assets and dependencies from the root README.
2. Run `.venv/bin/python scripts/compose-ravenclaw-study.py` to rebuild the hybrid atlas from the saved generated sources.
3. Export it with `scripts/wrap.py export --model modely --source public/studies/ravenclaw/atlas-C-registered.png --name Raven_Celestial_v4.png --base '#10243c' --id raven-celestial-v4 --title 'Ravenclaw celestial v4'`.
4. Run `npm run review -- --model modely --wrap raven-celestial-v4 --out artifacts/ravenclaw-v4`, inspect all images and validate the capture evidence.

`prompts.json`, `correction-v2.txt` and `remove-handles-v3.txt` preserve the generation instructions. Source images remain separate from the final PNG. The exact Tesla template is downloaded at setup rather than bundled here; the labeled guide is a local derivative of that template.
