# Validation and quality passes

Release candidate checked on 2026-10-01. These are local software and rendering checks, not proof of acceptance by Tesla firmware.

## Pass 1: artwork fidelity and export integrity

The original exporter always reduced colour to a 256-entry palette; it now preserves RGB when it fits the 1,000,000-byte limit and uses quantization only as a fallback. The example composer now preserves emblem aspect ratio. Rectangular atlases are rejected instead of silently stretched. Candidate bytes are validated before replacing an existing export. Example builds always use the committed source, not an optional local scratch file.

Nine Python tests cover resizing/model binding, source preservation, overwrite protection, filenames, invalid PNG/dimensions, metadata tampering, rectangular atlas rejection, full-colour preservation and failed replacement safety and stale screenshot rejection. Three Node tests cover all five model families, all house/Express exports, checksums and safe filenames.

## Pass 2: browser behavior and visual evidence

The real browser check passes at 320, 390, 768 and 1440px without horizontal overflow. It checks byte-exact catalogue and custom downloads, invalid-upload recovery, rapid model switching, stale custom-upload URL removal, local-only runtime requests and absence of browser exceptions. The viewer now explicitly exposes pending/ready/error state so an agent cannot mistake a previous render for the requested one.

`npm run review -- --all` captured 27 exports from five angles (135 images) with no browser errors. `examples/reviews/capture.json` binds those views to PNG hashes. `python3 scripts/wrap.py validate-review examples/reviews/capture.json` checks that the evidence has not become stale. Capture alone leaves visual review pending; qualitative findings are recorded separately in the [review notes](../examples/reviews/README.md).

The installed Chrome fallback was used locally (`PLAYWRIGHT_CHANNEL=chrome`) after Playwright's managed-browser CDN download timed out. Both browser checks and the full capture sweep actually ran. CI uses Playwright's managed Chromium. Production build passes; Vite reports a non-blocking large Three.js bundle warning.

## Pass 3: portable setup and agent handoff

The skill bootstrap uses a lockfile fingerprint to reinstall dependencies when they change rather than merely checking that Three.js exists. Asset downloads remain pinned and checksum-checked. Source/skill archives exclude local paths, private reference photos, downloaded vehicle meshes/templates and runtime dependencies. A clean source ZIP was extracted into a new temporary directory: bootstrap downloaded all ten pinned assets, installed Node/Python dependencies, validated all 27 exports, passed Node tests and built the viewer successfully.

The independent skill forward-test confirmed the model clarification and existing-example workflow. Its first test observations preceded the addition of the test files; the tests listed above were subsequently run and passed. The skill frontmatter validator passes using an isolated PyYAML environment.

No example is in-car verified. Model-specific wheels and lighting remain approximate. Generated artwork is not a substitute for final on-vehicle inspection.
