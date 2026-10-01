# Imagegen → model-specific wrap → visual feedback

## 1. Lock the target

Select one id from `public/models.json`. Confirm body generation and trim, not just year or Long Range. Fetch assets with `npm run setup:assets`. Open `public/templates/<id>.png` and inspect it. Treat every other Model Y template as a different target.

## 2. Generate artwork, not a pretend preview

Use the built-in imagegen tool. A concept car image can explore a theme, but it is not a wrap and cannot establish fit. Then generate either a flat atlas using the exact template as a reference or reusable detailed motif tiles for measured placement. Always save source PNGs and the full prompt. Name background/reference/template roles explicitly. Ask for a flat map, exact island positions, quiet seam margins and no overall scene lighting.

The house examples demonstrate tile composition: imagegen supplies engraved animals/crests; code cuts, resizes, rotates and masks them onto separately defined model regions. Avoid replacing detailed generated artwork with basic canvas symbols. Full-body maps should generally be generated anew for each family; a mask alone cannot adapt one family's atlas to another.

## 3. Fit and validate

Use `.venv/bin/python scripts/wrap.py export --model <id> --source <atlas> --name <Name_v1.png> --base <hex> --id <slug-v1> --title <title>`. It writes a PNG and provenance JSON under `public/wraps/<model>/` and optionally registers a catalogue entry. PNG output is square 1024px and checked against the conservative 1MB limit. Full RGB colour is preserved if it fits; 256-colour quantization is only a fallback for oversized output. Rectangular input is rejected rather than silently stretched: compose it onto a square atlas first. Keep the higher-detail generated source separately.

The export helper cuts to the exact mask but does not infer what each illustrated piece represents. If a logo is sideways, rotate the logo tile, not the entire irregular door island. Never flood-fill all black pixels: that can destroy tyres, vents and grilles. Quiet background padding is preferable to harsh seams.

## 4. Inspect the actual mesh

Open the deep link `http://127.0.0.1:5178/?model=<id>&wrap=<slug-v1>`. Verify `window.studioState` and wait for both model and texture. Capture front/rear/left/right/top. Let two animation frames render after a camera change. Save view downloads the canvas for imagegen feedback; full-page screenshots document the controls and selected model.

For repeatable evidence, install the browser once with `npx playwright install chromium`, then run:

```sh
npm run review -- --model modely --wrap ravenclaw --out artifacts/ravenclaw/modely/review-v1
```

This starts its own temporary local viewer, verifies the selected model/design and mapped paint meshes, and captures all five angles plus `capture.json` with PNG and screenshot hashes. Inspect the images; the report deliberately leaves visual review pending. Use `--all` for a catalogue sweep. If browser download is unavailable but Google Chrome is installed, prefix the command with `PLAYWRIGHT_CHANNEL=chrome` on macOS/Linux (PowerShell: `$env:PLAYWRIGHT_CHANNEL='chrome'`).

Look for stretching, reversed text, upside-down heraldry, duplicate trim, unpaintable glass, wrongly placed roof rails, high front grilles, misaligned seams and tiny details lost at 1024px. Record both what works and what fails. Local rendering is not in-car validation.

## 5. Feed the evidence back

Send imagegen the current atlas, actual viewer screenshots and exact model template. Ask for a short list of precise corrections, such as shrinking a grille 30%, moving carbon strips to the outer atlas edges, rotating louvres to appear horizontal or keeping a quiet 12px margin. Export as v2, inspect again and keep v1 available for comparison. Do not claim a refinement happened unless the next source was generated using the observed evidence.

For new designs, the skill ordinarily does one correction pass; further passes are justified by observed defects. Stop after three correction passes with a clear account of remaining limitations, unless the user asks to continue. Existing examples need not be regenerated merely to download them.

## 6. Review record and handoff

Store prompts and source images under `artifacts/<design>/<model>/` for user work. Keep selected public examples and review evidence under `examples/`. Update the sidecar's `visualReview` and catalogue status only with observations actually made; leave `inCarVerified` false until user evidence exists. Use `validate-catalog` to check files and binding hashes. Run `validate-review <path/to/capture.json>` before reusing screenshot evidence: it fails if the PNG or any view changed.

Give the user the local preview, exact model, PNG path and size, remaining fit limits and [Tesla installation steps](TESLA-INSTALL.md). Do not publish, write to USB or operate the car merely because a wrap was created.
