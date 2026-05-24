from __future__ import annotations

import sys
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from floravision.identifier import FloraIdentifier, ModelUnavailableError


class FallbackIdentifier(FloraIdentifier):
    def _identify_with_clip(self, image):  # type: ignore[no-untyped-def]
        raise ModelUnavailableError("test fallback")


class IdentifierTests(unittest.TestCase):
    def test_obviously_blank_non_flora_image_is_rejected(self) -> None:
        result = FallbackIdentifier().identify(Image.new("RGB", (96, 96), (20, 20, 20)))

        self.assertEqual(result["status"], "rejected_non_flora")
        self.assertIn("Only flora images are allowed", result["rejection_message"])
        self.assertEqual(result["category"], "non-flora image")


if __name__ == "__main__":
    unittest.main()

