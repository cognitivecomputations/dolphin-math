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

from arithmetic.generators.decimal_mult_generator import DecimalMultGenerator
from arithmetic.helpers import DELIM

class TestDecimalMultGenerator(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        self.generator = DecimalMultGenerator()
        # random.seed(43) # Optional: for predictable tests

    def test_generate_output_format(self):
        """Test the output format of the generate method."""
        result = self.generator.generate()

        self.assertIsInstance(result, dict)
        self.assertIn("problem_id", result)
        self.assertIsInstance(result["problem_id"], str)
        self.assertIn("operation", result)
        self.assertEqual(result["operation"], "decimal_mul")
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
        has_setup_step = any(s.startswith(f"MUL_SETUP{DELIM}") for s in result["steps"])
        has_partial_step = any(s.startswith(f"MUL_PARTIAL{DELIM}") for s in result["steps"])
        has_add_step = any(s.startswith(f"ADD_PARTIALS{DELIM}") for s in result["steps"])
        has_count_step = any(s.startswith(f"COUNT_DP{DELIM}") for s in result["steps"])
        has_place_step = any(s.startswith(f"PLACE_DP{DELIM}") for s in result["steps"])
        self.assertTrue(has_setup_step, "Missing MUL_SETUP step")
        self.assertTrue(has_partial_step, "Missing MUL_PARTIAL step")
        self.assertTrue(has_add_step, "Missing ADD_PARTIALS step")
        self.assertTrue(has_count_step, "Missing COUNT_DP step")
        self.assertTrue(has_place_step, "Missing PLACE_DP step")


    def test_generate_consistency(self):
        """Generate multiple examples and check basic consistency."""
        for _ in range(10): # Generate a few examples
            result = self.generator.generate()
            # Re-run basic format checks (includes final step check)
            self.test_generate_output_format() # Reuse format check

            # Check if problem string looks reasonable
            self.assertIn("*", result["problem"])
            self.assertIn("problem_id", result)
            self.assertIn("operation", result)
            self.assertIn("problem", result)
            self.assertIn("steps", result)
            self.assertIn("final_answer", result)
            self.assertGreater(len(result["steps"]), 0)
            self.assertTrue(result["steps"][-1].startswith(f"Z{DELIM}"))
            self.assertEqual(result["steps"][-1].split(DELIM)[1], result["final_answer"])

            # Check if problem string looks reasonable
            self.assertIn("*", result["problem"])
            # Check if final answer is a valid number string
            try:
                float(result["final_answer"])
            except ValueError:
                self.fail(f"Final answer '{result['final_answer']}' is not a valid number string.")

if __name__ == '__main__':
    unittest.main()
