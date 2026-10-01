# Mapped review evidence

`capture.json` records 31 catalogue exports from five camera views each, with hashes of the actual PNGs and all 155 raw screenshots. The screenshots contain only WebGL canvas pixels, without viewer controls. Run `python3 scripts/wrap.py validate-review examples/reviews/capture.json` to reject stale evidence. Capture is automated; qualitative visual review is separate.

On 2026-10-01, front, rear, left, right and top contact sheets were visually inspected for the rich Hogwarts Express and four house designs on all five bodies (25 exports). Hood motifs and side engravings occupy the intended surfaces, glass and wheels retain their materials, and no major missing paint island was apparent at contact-sheet scale. The Express locomotive is upright and faces forward on both sides after a screenshot-guided generation/composition correction. Small seam discontinuities, scale changes between panels and loss of fine detail remain. See the [artwork and correction notes](../artwork/rich-collection/README.md).

The six earlier study exports were captured for regression and clean presentation; this pass does not grant them new visual approval. Historical Ravenclaw comparison measurements and their original captures remain in `public/studies/ravenclaw`; its presentation page now displays clean car-only derivatives of the current raw captures. No design has been verified inside a Tesla.

`python3 scripts/build-showcase.py` checks evidence hashes before making cropped/padded showcase derivatives in `public/gallery/cars` and `docs/screenshots`. These contain the real mapped car; no AI beautification is applied to rendered screenshots.
