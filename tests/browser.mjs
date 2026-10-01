import assert from "node:assert/strict";
import { chromium } from "playwright";
import { createServer } from "vite";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";
const root = fileURLToPath(new URL("../", import.meta.url));
const server = await createServer({
  root,
  server: { host: "127.0.0.1", port: 0 },
});
let browser;
try {
  await server.listen();
  browser = await chromium.launch({
    channel: process.env.PLAYWRIGHT_CHANNEL || undefined,
  });
  const page = await browser.newPage(),
    errors = [],
    external = [];
  page.setDefaultTimeout(30000);
  page.on("pageerror", (e) => {
    errors.push(e.message);
    console.error(e.message);
  });
  page.on("request", (r) => {
    if (
      /^https?:/.test(r.url()) &&
      !r.url().startsWith(server.resolvedUrls.local[0])
    )
      external.push(r.url());
  });
  await page.goto(
    server.resolvedUrls.local[0] + "?model=modely&wrap=ravenclaw",
  );
  await page.waitForFunction(
    () => window.studioState?.ready || window.studioState?.error,
  );
  assert.equal(await page.evaluate(() => window.studioState?.error), undefined);
  console.log("Initial model ready");
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth),
      width,
      `overflow at ${width}`,
    );
  }
  const original = await readFile(
    path.join(root, "public/wraps/modely/Ravenclaw_Rich.png"),
  );
  await page.locator('[data-camera="left"]').click();
  await page.waitForTimeout(450);
  const probes = await page.evaluate(() => ({
    door: window.studioProbe(0.56, 0.55),
    glass: window.studioProbe(0.53, 0.39),
    background: window.studioProbe(0.05, 0.05),
    invalid: window.studioProbe(-1, 0.5),
  }));
  assert.equal(probes.door.paintable, true);
  assert.ok(probes.door.pixel.every((v) => v >= 0 && v <= 1024));
  assert.equal(probes.glass.paintable, false);
  assert.equal(probes.glass.pixel, null);
  assert.equal(probes.background, null);
  assert.equal(probes.invalid, null);
  console.log("Surface probe and layout checks passed");
  const downloadPromise = page.waitForEvent("download");
  await page.locator("#download").click();
  assert.deepEqual(
    await readFile(await (await downloadPromise).path()),
    original,
    "download must preserve PNG bytes",
  );
  await page.locator("#upload").setInputFiles({
    name: "bad.png",
    mimeType: "image/png",
    buffer: Buffer.from("not a PNG"),
  });
  await page.waitForFunction(() => window.studioState?.error);
  assert.equal(await page.locator("#download").isDisabled(), true);
  await page.locator("#upload").setInputFiles({
    name: "My_Test.png",
    mimeType: "image/png",
    buffer: original,
  });
  await page.waitForFunction(
    () => window.studioState?.ready && window.studioState.wrap === "custom",
  );
  assert.equal(
    new URL(page.url()).searchParams.has("wrap"),
    false,
    "custom upload must not retain stale gallery link",
  );
  const customPromise = page.waitForEvent("download");
  await page.locator("#download").click();
  assert.deepEqual(
    await readFile(await (await customPromise).path()),
    original,
  );
  await page.locator("#model").selectOption("modely-2025-base");
  await page.locator("#model").selectOption("modely-l");
  await page.waitForFunction(
    () => window.studioState?.ready && window.studioState.model === "modely-l",
  );
  assert.ok((await page.evaluate(() => window.studioState)).wrapMeshes > 0);
  assert.equal(new URL(page.url()).searchParams.get("model"), "modely-l");
  await page.goto(
    server.resolvedUrls.local[0] + "studies/ravenclaw/index.html",
  );
  await page
    .locator("h1")
    .filter({ hasText: "Design for the body." })
    .waitFor();
  for (const view of ["front", "left", "right", "rear", "top"]) {
    await page.locator(`[data-camera="${view}"]`).click();
    await page.waitForFunction(() =>
      Array.from(document.querySelectorAll(".grid img")).every(
        (i) => i.complete && i.naturalWidth > 0,
      ),
    );
  }
  for (const width of [390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth),
      width,
    );
  }
  await page.goto(server.resolvedUrls.local[0] + "gallery/index.html");
  await page.waitForFunction(() => document.querySelectorAll("main img").length === 31);
  await page.evaluate(async () => {
    const images = Array.from(document.querySelectorAll("main img"));
    images.forEach(i => i.loading = "eager");
    await Promise.all(images.map(i => i.decode()));
  });
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width);
  }
  await page.locator("main a").first().click();
  await page.waitForFunction(() => window.studioState?.ready && window.studioState.wrap === "hogwarts");
  const raw = await page.evaluate(() => window.studioCapture());
  assert.ok(raw.startsWith("data:image/png;base64,"));
  assert.ok(Buffer.from(raw.split(",")[1], "base64").length > 10000, "capture contains rendered content");
  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  console.log(
    "Passed: responsive widths, byte-exact downloads, invalid/valid upload recovery, custom deep-link reset, rapid model switch, local-only runtime, comparison page cameras/layout, car-only gallery images/layout/links, raw WebGL capture, no browser exceptions.",
  );
} finally {
  await browser?.close();
  await server.close();
}
