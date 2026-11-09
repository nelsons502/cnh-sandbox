import unittest

from agenda import is_back_to_back, minutes_between


class AgendaTest(unittest.TestCase):
    def test_gap(self):
        self.assertEqual(minutes_between(690, 720), 30)

    def test_back_to_back(self):
        self.assertTrue(is_back_to_back(720, 725))
        self.assertFalse(is_back_to_back(720, 750))


if __name__ == "__main__":
    unittest.main()
