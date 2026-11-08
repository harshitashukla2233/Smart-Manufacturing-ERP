import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules.planning import validate_master_data, calculate_mrp, capacity_load

DATA = ROOT / "data"

class PlanningTests(unittest.TestCase):
    def test_master_data_validation_passes(self):
        checks = validate_master_data(DATA)
        self.assertTrue((checks.status == "PASS").all(), checks.to_string())

    def test_mrp_returns_expected_columns(self):
        result = calculate_mrp(DATA)
        expected = {"product_id","gross_requirement","net_requirement","action"}
        self.assertTrue(expected.issubset(result.columns))
        self.assertGreater(len(result), 0)

    def test_capacity_calculation_returns_utilisation(self):
        result = capacity_load(DATA, 100)
        self.assertIn("utilisation_pct", result.columns)
        self.assertTrue((result.required_hours >= 0).all())

if __name__ == "__main__":
    unittest.main()
