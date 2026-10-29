import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import SeedRecord, SeedTree

class SeedTreeTests(unittest.TestCase):
    def setUp(self):
        self.tree = SeedTree()
        for code in (410, 230, 610, 150, 320, 520, 720):
            self.tree.insert(SeedRecord(code, f"Species {code}", "Andes", "Estable", 80))

    def test_inorder_is_sorted(self):
        self.assertEqual([r.accession for r in self.tree.traverse("inorder")], [150, 230, 320, 410, 520, 610, 720])

    def test_duplicate_is_rejected(self):
        self.assertFalse(self.tree.insert(SeedRecord(410, "Duplicate", "Andes", "Estable", 80)))
        self.assertEqual(self.tree.size, 7)

    def test_search(self):
        self.assertEqual(self.tree.search(320).accession, 320)
        self.assertIsNone(self.tree.search(999))

    def test_delete_leaf_and_root(self):
        self.assertTrue(self.tree.delete(150))
        self.assertTrue(self.tree.delete(410))
        self.assertFalse(self.tree.delete(999))
        self.assertEqual([r.accession for r in self.tree.traverse()], [230, 320, 520, 610, 720])

    def test_metrics(self):
        self.assertEqual(self.tree.size, 7)
        self.assertGreaterEqual(self.tree.height(), 1)
        self.assertGreaterEqual(self.tree.leaves(), 1)

if __name__ == "__main__":
    unittest.main()
