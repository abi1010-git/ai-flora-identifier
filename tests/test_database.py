from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from floravision.database import clear_history, fetch_recent_searches, init_db, save_search


class DatabaseTests(unittest.TestCase):
    def test_save_fetch_and_clear_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "history.sqlite3"
            init_db(db_path)
            result = {
                "common_name": "Sunflower",
                "scientific_name": "Helianthus annuus",
                "category": "flower",
                "confidence": 0.42,
                "confidence_percent": "42.0%",
                "status": "identified",
                "model_used": "test-model",
            }
            row_id = save_search(db_path, b"image-bytes", "sunflower.jpg", result)
            self.assertEqual(row_id, 1)

            rows = fetch_recent_searches(db_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["common_name"], "Sunflower")
            self.assertEqual(rows[0]["result"]["model_used"], "test-model")

            clear_history(db_path)
            self.assertEqual(fetch_recent_searches(db_path), [])


if __name__ == "__main__":
    unittest.main()

