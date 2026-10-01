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
  page.on("pageerror", (e) => errors.push(e.message));
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
  await page.waitForFunction(() => window.studioState?.ready);
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth),
      width,
      `overflow at ${width}`,
    );
  }
  const original = await readFile(
    path.join(root, "public/wraps/modely/Ravenclaw.png"),
  );
  const downloadPromise = page.waitForEvent("download");
  await page.locator("#download").click();
  assert.deepEqual(
    await readFile(await (await downloadPromise).path()),
    original,
    "download must preserve PNG bytes",
  );
  await page
    .locator("#upload")
    .setInputFiles({
      name: "bad.png",
      mimeType: "image/png",
      buffer: Buffer.from("not a PNG"),
    });
  await page.waitForFunction(() => window.studioState?.error);
  assert.equal(await page.locator("#download").isDisabled(), true);
  await page
    .locator("#upload")
    .setInputFiles({
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
  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  console.log(
    "Passed: responsive widths, byte-exact downloads, invalid/valid upload recovery, custom deep-link reset, rapid model switch, local-only runtime, no browser exceptions.",
  );
} finally {
  await browser?.close();
  await server.close();
}
