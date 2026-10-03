"""Unit tests for the scanner module using unittest."""

import unittest
from antigravity_restore.scanner import clean_title


class TestScanner(unittest.TestCase):
    def test_clean_title(self):
        self.assertEqual(clean_title("<USER_REQUEST> how to train GNN?"), "how to train GNN?")
        self.assertEqual(clean_title("### Refactor model architecture"), "Refactor model architecture")
        self.assertEqual(clean_title("First line\nSecond line"), "First line")
        self.assertEqual(clean_title(""), "Untitled Conversation")


if __name__ == "__main__":
    unittest.main()
