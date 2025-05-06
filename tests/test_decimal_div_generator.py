import unittest
import sys
import os
import random

# Add parent directory to path to allow importing 'arithmetic' modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir) # Go up two levels
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

from arithmetic.generators.decimal_div_generator import DecimalDivGenerator
from arithmetic.helpers import DELIM

class TestDecimalDivGenerator(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        self.generator = DecimalDivGenerator()
        # random.seed(44) # Optional: for predictable tests

    def test_generate_output_format(self):
        """Test the output format of the generate method."""
        result = self.generator.generate()

        self.assertIsInstance(result, dict)
        self.assertIn("problem_id", result)
        self.assertIsInstance(result["problem_id"], str)
        self.assertIn("operation", result)
        self.assertEqual(result["operation"], "decimal_div")
        self.assertIn("problem", result)
        self.assertIsInstance(result["problem"], str)
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
        # Check for detailed steps
        has_shift_step = any(s.startswith(f"DEC_SHIFT{DELIM}") for s in result["steps"])
        has_setup_step = any(s.startswith(f"DIV_SETUP{DELIM}") for s in result["steps"])
        has_long_div_steps = any(s.startswith(f"D{DELIM}") or s.startswith(f"M{DELIM}") or s.startswith(f"S{DELIM}") or s.startswith(f"B{DELIM}") for s in result["steps"])
        has_place_dp_step = any(s.startswith(f"PLACE_DP_Q{DELIM}") for s in result["steps"])

        self.assertTrue(has_shift_step, "Missing DEC_SHIFT step")
        self.assertTrue(has_setup_step, "Missing DIV_SETUP step")
        self.assertTrue(has_long_div_steps, "Missing core long division steps (D, M, S, B)")
        self.assertTrue(has_place_dp_step, "Missing PLACE_DP_Q step")

        # Check B step format (Args: Remainder Before, Digit Down, New Num)
        b_steps = [s for s in result["steps"] if s.startswith(f"B{DELIM}")]
        for b_step in b_steps:
            b_parts = b_step.split(DELIM)
            self.assertEqual(len(b_parts), 4, f"B step should have 4 parts: {b_step}")
            try:
                int(b_parts[1]) # Remainder before
                int(b_parts[2]) # Digit down
                int(b_parts[3]) # New num
            except ValueError:
                self.fail(f"B step arguments are not integers: {b_step}")


    def test_generate_consistency(self):
        """Generate multiple examples and check basic consistency."""
        for _ in range(10): # Generate a few examples
            result = self.generator.generate()
            # Re-run basic format checks (includes detailed step checks)
            self.test_generate_output_format()

            # Check if problem string looks reasonable
            self.assertIn("/", result["problem"]) # Check for division symbol
            self.assertIn("problem_id", result)
            self.assertIn("operation", result)
            self.assertIn("problem", result)
            self.assertIn("steps", result)
            self.assertIn("final_answer", result)
            self.assertGreater(len(result["steps"]), 0)
            self.assertTrue(result["steps"][-1].startswith(f"Z{DELIM}"))
            self.assertEqual(result["steps"][-1].split(DELIM)[1], result["final_answer"])

            # Check if problem string looks reasonable
            self.assertIn("/", result["problem"]) # Check for division symbol
            # Check if final answer is a valid number string
            try:
                float(result["final_answer"])
            except ValueError:
                self.fail(f"Final answer '{result['final_answer']}' is not a valid number string.")
            # Check if final answer is a valid number string
            try:
                float(result["final_answer"])
            except ValueError:
                self.fail(f"Final answer '{result['final_answer']}' is not a valid number string.")
            # Check first step is DEC_SHIFT
            self.assertTrue(result["steps"][0].startswith(f"DEC_SHIFT{DELIM}"), "First step should be DEC_SHIFT")


if __name__ == '__main__':
    unittest.main()
