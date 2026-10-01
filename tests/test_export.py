import importlib.util, json, tempfile, unittest
from pathlib import Path
from PIL import Image, ImageDraw
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "wrap", Path(__file__).parents[1] / "scripts/wrap.py"
)
wrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrap)


class ExportContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.patch = patch.object(wrap, "ROOT", self.root)
        self.patch.start()
        (self.root / "public/templates").mkdir(parents=True)
        (self.root / "public/models.json").write_text(json.dumps([{"id": "modely"}]))
        mask = Image.new("RGB", (1024, 1024), "black")
        ImageDraw.Draw(mask).rectangle((100, 100, 900, 900), fill="white")
        mask.save(self.root / "public/templates/modely.png")
        self.source = self.root / "source.png"
        Image.new("RGB", (1254, 1254), "red").save(self.source)

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def test_resize_bind_and_preserve_source(self):
        before = wrap.digest(self.source)
        out, meta = wrap.export_image(self.source, "modely", "Test_v1.png", "#123456")
        with Image.open(out) as image:
            self.assertEqual(image.size, (1024, 1024))
            self.assertEqual(image.convert("RGB").getpixel((0, 0)), (18, 52, 86))
        self.assertEqual(meta["model"], "modely")
        self.assertFalse(meta["inCarVerified"])
        self.assertEqual(before, wrap.digest(self.source))
        self.assertLess(out.stat().st_size, 1_000_000)
        wrap.register("test", "Test", "modely", out)
        wrap.validate_catalog()

    def test_refuses_overwrite_and_bad_model(self):
        wrap.export_image(self.source, "modely", "Test.png")
        with self.assertRaises(ValueError):
            wrap.export_image(self.source, "modely", "Test.png")
        with self.assertRaises(ValueError):
            wrap.export_image(self.source, "wrong-model", "Test2.png")

    def test_rejects_path_and_oversize_names(self):
        for name in ["../Escape.png", "a" * 27 + ".png", "emoji🚗.png", "test.jpg"]:
            with self.assertRaises(ValueError):
                wrap.valid_name(name)

    def test_rejects_wrong_dimensions_and_format(self):
        for size in [(1024, 512), (2048, 2048), (256, 256)]:
            p = self.root / "Bad.png"
            Image.new("RGB", size).save(p)
            with self.assertRaises(ValueError):
                wrap.validate(p)
        p = self.root / "Fake.png"
        Image.new("RGB", (1024, 1024)).save(p, format="JPEG")
        with self.assertRaises(ValueError):
            wrap.validate(p)

    def test_detects_model_binding_tampering(self):
        out, meta = wrap.export_image(self.source, "modely", "Test.png")
        wrap.register("test", "Test", "modely", out)
        meta["model"] = "modely-l"
        out.with_suffix(".json").write_text(json.dumps(meta))
        with self.assertRaises(ValueError):
            wrap.validate_catalog()

    def test_rejects_rectangular_atlas_without_creating_output(self):
        Image.new("RGB", (1200, 800)).save(self.source)
        with self.assertRaisesRegex(ValueError, "square"):
            wrap.export_image(self.source, "modely", "Rectangle.png")
        self.assertFalse((self.root / "public/wraps/modely/Rectangle.png").exists())

    def test_preserves_full_colour_when_under_limit(self):
        image = Image.new("RGB", (1024, 1024))
        image.putdata(
            [(x % 256, (x // 1024) % 256, (x // 13) % 256) for x in range(1024 * 1024)]
        )
        image.save(self.source)
        out, meta = wrap.export_image(self.source, "modely", "Colour.png")
        self.assertEqual(meta["encoding"], "RGB")
        with Image.open(out) as result:
            self.assertEqual(result.mode, "RGB")
            self.assertGreater(len(result.getcolors(1024 * 1024)), 256)

    def test_failed_replace_preserves_good_export(self):
        out, _ = wrap.export_image(self.source, "modely", "Good.png")
        before = out.read_bytes()
        self.source.write_bytes(b"invalid image")
        with self.assertRaises(OSError):
            wrap.export_image(self.source, "modely", "Good.png", replace=True)
        self.assertEqual(out.read_bytes(), before)

    def test_rejects_stale_review_evidence(self):
        out, _ = wrap.export_image(self.source, "modely", "Review.png")
        wrap.register("review", "Review", "modely", out)
        shot = self.root / "front.png"
        Image.new("RGB", (20, 20)).save(shot)
        report = {
            "errors": [],
            "records": [
                {
                    "model": "modely",
                    "wrap": "review",
                    "pngFile": "/wraps/modely/Review.png",
                    "pngSha256": wrap.digest(out),
                    "views": {
                        v: {"file": "front.png", "sha256": wrap.digest(shot)}
                        for v in ["front", "rear", "left", "right", "top"]
                    },
                }
            ],
        }
        file = self.root / "capture.json"
        file.write_text(json.dumps(report))
        wrap.validate_review(file)
        Image.new("RGB", (1024, 1024), "blue").save(out)
        with self.assertRaisesRegex(ValueError, "Stale capture"):
            wrap.validate_review(file)


if __name__ == "__main__":
    unittest.main()
