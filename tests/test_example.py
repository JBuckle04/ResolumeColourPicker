import unittest

class TestSum(unittest.TestCase):

    def test_sum(self):
        self.assertEqual(1+2+3, 6, "Should be 6")

if __name__ == "__main_":
    unittest.main()