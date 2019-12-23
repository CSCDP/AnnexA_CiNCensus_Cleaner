import unittest
import os
from fddc.annex_a.merger import *

class TestMerger(unittest.TestCase):

    def test_parse_config(self):
        self.assertEqual(parse_input_config("test"), [{"root": os.getcwd(), "include": "test"}])

        self.assertEqual(parse_input_config(["test2"]), [{"root": os.getcwd(), "include": "test2"}])

        self.assertEqual(
            parse_input_config(dict(include='test3')),
            [{"root": os.getcwd(), "include": "test3"}]
        )

        self.assertEqual(
            parse_input_config(dict(root='./sample', include='test4')),
            [{"root": './sample', "include": "test4"}]
        )

        self.assertEqual(
            parse_input_config(["test5", dict(include="test6")]),
            [dict(root=os.getcwd(), include="test5"), dict(root=os.getcwd(), include="test6")]
        )

        self.assertEqual(parse_input_config("include"), [{"root": os.getcwd(), "include": "include"}])

        self.assertEqual(parse_input_config(["include"]), [{"root": os.getcwd(), "include": "include"}])
