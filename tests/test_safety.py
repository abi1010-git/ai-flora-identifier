from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from floravision.catalog import load_catalog
from floravision.config import DEFAULT_CATALOG_PATH
from floravision.safety import (
    LOW_CONFIDENCE_MESSAGE,
    REQUIRED_DISCLAIMER,
    confidence_status,
    contains_forbidden_safety_claim,
    low_confidence_message,
)


class SafetyTests(unittest.TestCase):
    def test_required_messages(self) -> None:
        self.assertEqual(REQUIRED_DISCLAIMER, "AI identification may be incorrect.")
        self.assertEqual(low_confidence_message(0.01, 0.17), LOW_CONFIDENCE_MESSAGE)
        self.assertIsNone(low_confidence_message(0.25, 0.17))
        self.assertEqual(confidence_status(0.25, 0.17), "identified")
        self.assertEqual(confidence_status(0.03, 0.17), "low_confidence")

    def test_catalog_avoids_forbidden_safety_claims(self) -> None:
        species = load_catalog(DEFAULT_CATALOG_PATH)
        for item in species:
            self.assertFalse(
                contains_forbidden_safety_claim(item.toxicity_note),
                item.common_name,
            )


if __name__ == "__main__":
    unittest.main()

