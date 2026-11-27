import unittest
import numpy as np
from math_engine.linear_algebra import gaussian_elimination, matrix_rank, null_space

class TestGaussianElimination(unittest.TestCase):
    def test_normal(self):
        r, p, _, _, _ = gaussian_elimination([[2,1],[1,1]],[5,3])
        self.assertAlmostEqual(r[0][-1], 2)
        self.assertAlmostEqual(r[1][-1], 1)
    def test_pivot_edge(self):
        r, p, _, _, _ = gaussian_elimination([[0,1],[1,1]],[2,3])
        self.assertEqual(p, [0,1])
        self.assertAlmostEqual(r[0][-1], 1)
    def test_library_validation(self):
        A=[[3,1],[1,2]]; b=[9,8]
        r, _, _, _, _=gaussian_elimination(A,b)
        self.assertTrue(np.allclose([r[0][-1],r[1][-1]], np.linalg.solve(A,b)))

class TestRank(unittest.TestCase):
    def test_normal(self): self.assertEqual(matrix_rank([[1,2],[3,4]]),2)
    def test_dependent_edge(self): self.assertEqual(matrix_rank([[1,2],[2,4]]),1)
    def test_library_validation(self): self.assertEqual(matrix_rank([[1,2,3],[2,4,6]]),np.linalg.matrix_rank([[1,2,3],[2,4,6]]))

class TestNullSpace(unittest.TestCase):
    def test_normal(self):
        basis=null_space([[1,1]])
        self.assertEqual(len(basis),1)
        self.assertTrue(np.allclose(np.dot([[1,1]],basis[0]),[0]))
    def test_zero_matrix_edge(self):
        basis=null_space([[0,0],[0,0]])
        self.assertEqual(len(basis),2)
    def test_library_validation(self):
        A=np.array([[1.,2.,3.],[2.,4.,6.]])
        basis=null_space(A.tolist())
        self.assertEqual(len(basis), A.shape[1]-np.linalg.matrix_rank(A))
        for v in basis: self.assertTrue(np.allclose(A@v,0))

if __name__ == "__main__": unittest.main()
