/** Reproducible real-WebGL evidence; captured does not mean visually approved. */
import { chromium } from "playwright";
import { createServer } from "vite";
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2),
  value = (key) => args[args.indexOf(key) + 1];
const all = args.includes("--all");
if (!all && (!args.includes("--model") || !args.includes("--wrap")))
  throw new Error(
    "Use --model <id> --wrap <id>, or --all. Optional --out <directory>.",
  );
const catalog = JSON.parse(
  await readFile(path.join(root, "public/catalog.json")),
);
const targets = catalog
  .flatMap((w) =>
    Object.keys(w.models).map((model) => ({
      model,
      wrap: w.id,
      entry: w.models[model],
    })),
  )
  .filter(
    (t) => all || (t.model === value("--model") && t.wrap === value("--wrap")),
  );
if (!targets.length) throw new Error("No matching model/design in catalogue.");
const out = path.resolve(
  args.includes("--out") ? value("--out") : path.join(root, "artifacts/review"),
);
await mkdir(out, { recursive: true });
const server = await createServer({
  root,
  server: { host: "127.0.0.1", port: 0 },
});
let browser;
try {
  await server.listen();
  const origin = server.resolvedUrls.local[0];
  browser = await chromium.launch({
    headless: true,
    channel: process.env.PLAYWRIGHT_CHANNEL || undefined,
  });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
    deviceScaleFactor: 1,
  });
  page.setDefaultTimeout(30000);
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("response", (r) => {
    if (r.status() >= 400) errors.push(`${r.status()} ${r.url()}`);
  });
  const records = [];
  for (const t of targets) {
    await page.goto(`${origin}?model=${t.model}&wrap=${t.wrap}`);
    await page.waitForFunction(
      (t) =>
        window.studioState?.ready &&
        window.studioState.model === t.model &&
        window.studioState.wrap === t.wrap &&
        window.studioState.wrapMeshes > 0,
      t,
    );
    const state = await page.evaluate(() => window.studioState),
      views = {};
    for (const camera of ["front", "rear", "left", "right", "top"]) {
      await page.locator(`[data-camera="${camera}"]`).click();
      // OrbitControls damping must settle, then allow the painted texture to render.
      await page.waitForTimeout(350);
      await page.evaluate(
        () =>
          new Promise((r) =>
            requestAnimationFrame(() => requestAnimationFrame(r)),
          ),
      );
      const filename = `${t.model}-${t.wrap}-${camera}.png`;
      const bytes = await page
        .locator("#viewer canvas")
        .screenshot({ path: path.join(out, filename) });
      views[camera] = {
        file: filename,
        sha256: createHash("sha256").update(bytes).digest("hex"),
      };
    }
    const png = await readFile(path.join(root, "public", t.entry.file));
    records.push({
      ...state,
      pngFile: t.entry.file,
      pngSha256: createHash("sha256").update(png).digest("hex"),
      views,
      visualReview: "pending",
      inCarVerified: false,
    });
    console.log(`Captured ${t.model}/${t.wrap}: five views`);
  }
  const report = { capturedAt: new Date().toISOString(), errors, records };
  await writeFile(
    path.join(out, "capture.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  if (errors.length) throw new Error(`Browser errors: ${errors.join("; ")}`);
  console.log(
    `Evidence: ${out}. Inspect images and record findings before claiming visual approval.`,
  );
} finally {
  await browser?.close();
  await server.close();
}
