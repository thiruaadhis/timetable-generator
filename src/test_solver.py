import unittest
import solver


class TestSolver(unittest.TestCase):

    def test_solver_runs(self):
        try:
            solver.main()
        except Exception as e:
            self.fail(f"Solver failed: {e}")


if __name__ == "__main__":
    unittest.main()