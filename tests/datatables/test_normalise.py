import unittest
from fddc.datatables import normalise
import pandas as pd


class TestNormalise(unittest.TestCase):

    def test_create_new(self):
        df = normalise.normalise_dataframe(None, ["A", "B", "C"])

        self.assertIsNotNone(df)
        self.assertSequenceEqual(["A", "B", "C"], list(df.columns))

    def test_rename_and_reorder(self):
        df = pd.DataFrame(columns=["A", "B", "C"], data=[["A", "B", "C"]])

        df_n = normalise.normalise_dataframe(df, ["O", "B", "A", "F", "G", "K", "M"], dict(C="K"))
        self.assertListEqual(["O", "B", "A", "F", "G", "K", "M"], list(df_n.columns))

        df = normalise.normalise_dataframe(df, ["O", "B", "A", "F", "G", "K", "M"], dict(C="K"),
                                           only_retain_mapped=False)
        self.assertListEqual(["O", "B", "A", "F", "G", "K", "M"], list(df.columns))

        values = df.to_dict(orient="records")[0]
        self.assertEqual("A", values["A"])
        self.assertEqual("B", values["B"])
        self.assertEqual("C", values["K"])
