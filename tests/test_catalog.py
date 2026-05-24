from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from floravision.catalog import catalog_categories, load_catalog
from floravision.config import DEFAULT_CATALOG_PATH


class CatalogTests(unittest.TestCase):
    def test_catalog_covers_required_flora_types(self) -> None:
        species = load_catalog(DEFAULT_CATALOG_PATH)
        categories = catalog_categories(species)
        expected = {
            "leaf",
            "plant",
            "flower",
            "tree",
            "mushroom",
            "fungus",
            "moss",
            "grass",
            "shrub",
            "vine",
            "fruit",
            "seed",
            "cactus",
            "succulent",
            "aquatic plant",
        }
        self.assertTrue(expected.issubset(categories))

    def test_catalog_prompts_are_non_empty(self) -> None:
        species = load_catalog(DEFAULT_CATALOG_PATH)
        self.assertGreater(len(species), 10)
        for item in species:
            self.assertIn(item.common_name, item.prompt())
            self.assertIn(item.category, item.prompt())


if __name__ == "__main__":
    unittest.main()

