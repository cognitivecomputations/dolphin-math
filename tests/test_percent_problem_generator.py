import unittest
import sys
import os
import random
from decimal import Decimal # Needed for checking final answer type

# Add parent directory to path to allow importing 'arithmetic' modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir) # Go up two levels
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

from arithmetic.generators.percent_problem_generator import PercentProblemGenerator
from arithmetic.helpers import DELIM

class TestPercentProblemGenerator(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        self.generator = PercentProblemGenerator()
        # random.seed(55) # Optional: for predictable tests

    def test_generate_output_format(self):
        """Test the output format of the generate method."""
        result = self.generator.generate()

        self.assertIsInstance(result, dict)
        self.assertIn("problem_id", result)
        self.assertIsInstance(result["problem_id"], str)
        self.assertIn("operation", result)
        self.assertTrue(result["operation"].startswith("percent_"), "Operation name should start with 'percent_'")
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

        # Check for core percent steps based on operation type
        op = result["operation"]
        steps_str = "|".join(result["steps"]) # For easier searching

        if op == "percent_find_part":
            self.assertIn(f"PERCENT_TO_DEC{DELIM}", steps_str, "Missing PERCENT_TO_DEC")
            self.assertIn(f"SETUP_PERCENT_EQ{DELIM}", steps_str, "Missing SETUP_PERCENT_EQ")
            self.assertIn(f"PERCENT_CALC_PART{DELIM}", steps_str, "Missing PERCENT_CALC_PART")
            # Ensure no division steps are present for find_part
            self.assertNotIn(f"DEC_SHIFT{DELIM}", steps_str, "DEC_SHIFT should not be in find_part")
            self.assertNotIn(f"DIV_SETUP{DELIM}", steps_str, "DIV_SETUP should not be in find_part")
        elif op == "percent_find_percent":
            self.assertIn(f"SETUP_PERCENT_EQ{DELIM}", steps_str, "Missing SETUP_PERCENT_EQ")
            # Check for division steps
            self.assertIn(f"DEC_SHIFT{DELIM}", steps_str, "Missing DEC_SHIFT")
            self.assertIn(f"DIV_SETUP{DELIM}", steps_str, "Missing DIV_SETUP")
            self.assertTrue(any(s.startswith(f"D{DELIM}") for s in result["steps"]), "Missing D step")
            self.assertTrue(any(s.startswith(f"M{DELIM}") for s in result["steps"]), "Missing M step")
            self.assertTrue(any(s.startswith(f"S{DELIM}") for s in result["steps"]), "Missing S step")
            self.assertIn(f"PLACE_DP_Q{DELIM}", steps_str, "Missing PLACE_DP_Q")
            # Check for final conversion step
            self.assertIn(f"DEC_TO_PERCENT{DELIM}", steps_str, "Missing DEC_TO_PERCENT")
            # Ensure calculation steps specific to other types are not present
            self.assertNotIn(f"PERCENT_CALC_PART{DELIM}", steps_str)
            self.assertNotIn(f"PERCENT_CALC_WHOLE{DELIM}", steps_str)
            self.assertNotIn(f"REARRANGE_EQ{DELIM}", steps_str)
        elif op == "percent_find_whole":
            self.assertIn(f"PERCENT_TO_DEC{DELIM}", steps_str, "Missing PERCENT_TO_DEC")
            self.assertIn(f"SETUP_PERCENT_EQ{DELIM}", steps_str, "Missing SETUP_PERCENT_EQ")
            self.assertIn(f"REARRANGE_EQ{DELIM}", steps_str, "Missing REARRANGE_EQ")
            # Check for division steps
            self.assertIn(f"DEC_SHIFT{DELIM}", steps_str, "Missing DEC_SHIFT")
            self.assertIn(f"DIV_SETUP{DELIM}", steps_str, "Missing DIV_SETUP")
            self.assertTrue(any(s.startswith(f"D{DELIM}") for s in result["steps"]), "Missing D step")
            self.assertTrue(any(s.startswith(f"M{DELIM}") for s in result["steps"]), "Missing M step")
            self.assertTrue(any(s.startswith(f"S{DELIM}") for s in result["steps"]), "Missing S step")
            self.assertIn(f"PLACE_DP_Q{DELIM}", steps_str, "Missing PLACE_DP_Q")
            # Ensure calculation steps specific to other types are not present
            self.assertNotIn(f"PERCENT_CALC_PART{DELIM}", steps_str)
            self.assertNotIn(f"PERCENT_CALC_PERCENT{DELIM}", steps_str)
            self.assertNotIn(f"DEC_TO_PERCENT{DELIM}", steps_str)
        else:
            self.fail(f"Unknown percent operation type: {op}")

    def test_generate_consistency(self):
        """Generate multiple examples and check basic consistency."""
        for _ in range(10): # Generate a few examples
            result = self.generator.generate()
            # Re-run basic format checks (includes step checks)
            self.test_generate_output_format()

            # Check if problem string looks reasonable based on type
            op = result["operation"]
            problem = result["problem"]
            if op == "percent_find_part":
                self.assertIn("What is", problem)
                self.assertIn("% of", problem)
            elif op == "percent_find_percent":
                self.assertIn("is what percent of", problem)
            elif op == "percent_find_whole":
                 self.assertIn("is", problem)
                 self.assertIn("% of what number", problem)

            # Check final answer format
            final_answer = result["final_answer"]
            if op == "percent_find_percent":
                self.assertTrue(final_answer.endswith('%'), "Find Percent answer should end with %")
                try:
                    float(final_answer.rstrip('%'))
                except ValueError:
                    self.fail(f"Find Percent answer value '{final_answer}' is not valid.")
            else: # Find Part or Whole - should be a number
                 try:
                     Decimal(final_answer)
                 except InvalidOperation:
                     self.fail(f"Find Part/Whole answer '{final_answer}' is not a valid Decimal.")


if __name__ == '__main__':
    unittest.main()
