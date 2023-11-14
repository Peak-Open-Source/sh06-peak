import unittest
import sys
# sys.path.append("..")
from src.protein import Protein

class proteinTest(unittest.TestCase):
    
    def test_overlap(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(612, 711)
        test_protein.add_coverage(612, 713)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 101)
    
    def test_overlap_short(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(612, 650)
        test_protein.add_coverage(600, 625)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 50)
    
    def test_overlap_middle(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 650)
        test_protein.add_coverage(615, 640)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 35)
    
    def test_overlap_varied(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 650)
        test_protein.add_coverage(20, 50)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 50)
    
    def test_overlap_quad_merge(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 630)
        test_protein.add_coverage(615, 630)
        test_protein.add_coverage(640, 670)
        test_protein.add_coverage(610, 660)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 60)
    
    def test_overlap_merge_and_varied(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 650)
        test_protein.add_coverage(615, 640)
        test_protein.add_coverage(20, 50)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 65)

if __name__ == "__main__":
    unittest.main()