import unittest

import pandas as pd

from services.db_service import fetch_all_farmers, fetch_dataset_farmers


class DatasetProfileTests(unittest.TestCase):
    def test_farmer_profiles_are_loaded_from_current_csv_data(self):
        source = pd.read_csv("crop_data.csv")
        profiles = fetch_dataset_farmers()

        self.assertEqual(len(profiles), len(source))
        self.assertEqual(profiles[0]["farmer_id"], source.iloc[0]["Farmer_ID"])
        self.assertEqual(profiles[0]["crop_type"], source.iloc[0]["Crop_Type"])
        self.assertEqual(profiles[0]["rainfall_mm"], source.iloc[0]["Rainfall_mm"])
        self.assertEqual(fetch_all_farmers(), profiles)


if __name__ == "__main__":
    unittest.main()
