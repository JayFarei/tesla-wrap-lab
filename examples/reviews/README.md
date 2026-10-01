# Mapped review evidence

`capture.json` records 27 exports, five camera views each, and hashes of the actual PNGs and screenshots. Run `python3 scripts/wrap.py validate-review examples/reviews/capture.json` after changing artwork; it rejects stale evidence. Capture is automated, visual approval is not.

On 2026-10-01, five-angle contact sheets were visually inspected for all four house designs and Hogwarts Express on all five bodies. Hood motifs remain on the hood, crests read upright on both doors, glass/wheels retain their original materials, and no large clipped or missing emblem was apparent at contact-sheet scale. Small seams and tiny engraved detail were not certified pixel-perfect. Fine detail becomes less legible at car-display scale.

The quality pass preserved emblem proportions and removed mandatory 256-colour conversion before these captures. The original Express has a richer carriage/map layout; the other four bodies intentionally have simpler owl-emblem layouts. They are separate compositions, not equivalent full-body adaptations. Rear panels of the house designs are intentionally restrained.

F1 and Alpine were captured for regression evidence but were not included in the full qualitative contact-sheet review. They remain earlier original-body studies. All designs remain unverified in a Tesla. Glass reflections and preview illumination are viewer materials and cannot be controlled by the PNG.

For new designs, use these captures as examples of the evidence format, not as a replacement for capturing and inspecting the newly generated export. Record the observed fault, imagegen correction prompt, new source and new export before describing an iteration as screenshot-guided refinement.
