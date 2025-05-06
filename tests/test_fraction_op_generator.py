import unittest
import sys
import os
import random
from fractions import Fraction # Needed for checking final answer type

# Add parent directory to path to allow importing 'arithmetic' modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir) # Go up two levels
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

from arithmetic.generators.fraction_op_generator import FractionOpGenerator
from arithmetic.helpers import DELIM

class TestFractionOpGenerator(unittest.TestCase):

    def _run_basic_checks(self, result, expected_op_name_prefix, expected_op_symbol):
        """Helper function to run common checks."""
        self.assertIsInstance(result, dict)
        self.assertIn("problem_id", result)
        self.assertIsInstance(result["problem_id"], str)
        self.assertIn("operation", result)
        self.assertTrue(result["operation"].startswith(expected_op_name_prefix))
        self.assertIn("problem", result)
        self.assertIsInstance(result["problem"], str)
        self.assertIn(f" {expected_op_symbol} ", result["problem"]) # Check symbol in problem
        self.assertIn("steps", result)
        self.assertIsInstance(result["steps"], list)
        self.assertGreater(len(result["steps"]), 0, "Steps list should not be empty")
        self.assertIn("final_answer", result)
        self.assertIsInstance(result["final_answer"], str)

        # Check the final step format
        final_step = result["steps"][-1]
        self.assertTrue(final_step.startswith(f"Z{DELIM}"), f"Final step should start with Z{DELIM}")
        # Check if final answer in step matches the final_answer field
        self.assertEqual(final_step.split(DELIM)[1], result["final_answer"])
        # Check if final answer is a valid fraction string
        try:
            Fraction(result["final_answer"])
        except (ValueError, ZeroDivisionError):
            self.fail(f"Final answer '{result['final_answer']}' is not a valid Fraction string.")

    def test_generate_addition(self):
        """Test the generate method for fraction addition."""
        generator = FractionOpGenerator('+')
        for _ in range(10):
            result = generator.generate()
            self._run_basic_checks(result, "fraction_add", "+")

    def test_generate_subtraction(self):
        """Test the generate method for fraction subtraction."""
        generator = FractionOpGenerator('-')
        for _ in range(10):
            result = generator.generate()
            self._run_basic_checks(result, "fraction_sub", "-")

    def test_generate_multiplication(self):
        """Test the generate method for fraction multiplication."""
        generator = FractionOpGenerator('*')
        for _ in range(10):
            result = generator.generate()
            self._run_basic_checks(result, "fraction_mul", "*")

    def test_generate_division(self):
        """Test the generate method for fraction division."""
        generator = FractionOpGenerator('/')
        for _ in range(10):
            result = generator.generate()
            self._run_basic_checks(result, "fraction_div", "/")
            # Ensure divisor wasn't zero in the problem string
            problem_parts = result['problem'].split(' ')
            self.assertNotIn('/0', problem_parts[2], "Problem divisor fraction cannot have zero denominator") # Check denominator too
            # Check I step format
            i_step = next((s for s in result["steps"] if s.startswith(f"I{DELIM}")), None)
            self.assertIsNotNone(i_step, "Missing I step in division")
            if i_step:
                i_parts = i_step.split(DELIM)
                self.assertEqual(len(i_parts), 3, "I step should have 3 parts")
                self.assertIn('/', i_parts[2], "Inverted fraction in I step should contain '/'")


if __name__ == '__main__':
    unittest.main()
