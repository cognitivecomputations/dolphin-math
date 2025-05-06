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

from arithmetic.generators.decimal_add_sub_generator import DecimalAddSubGenerator
from arithmetic.helpers import DELIM

class TestDecimalAddSubGenerator(unittest.TestCase):

    def _run_basic_checks(self, result, expected_op_name, expected_op_symbol):
        """Helper function to run common checks."""
        self.assertIsInstance(result, dict)
        self.assertIn("problem_id", result)
        self.assertIsInstance(result["problem_id"], str)
        self.assertIn("operation", result)
        self.assertEqual(result["operation"], expected_op_name)
        self.assertIn("problem", result)
        self.assertIsInstance(result["problem"], str)
        self.assertIn(expected_op_symbol, result["problem"]) # Check symbol in problem
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
        # Check if final answer is a valid number string
        try:
            float(result["final_answer"])
        except ValueError:
            self.fail(f"Final answer '{result['final_answer']}' is not a valid number string.")
        # Check for detailed steps
        has_align_step = any(s.startswith(f"DEC_ALIGN{DELIM}") for s in result["steps"])
        col_op_steps = [s for s in result["steps"] if s.startswith(f"DEC_ADD_COL{DELIM}") or s.startswith(f"DEC_SUB_COL{DELIM}")]
        self.assertTrue(has_align_step, "Missing DEC_ALIGN step")
        self.assertTrue(len(col_op_steps) > 0, "Missing DEC_ADD_COL or DEC_SUB_COL step")
        # Check column name format in column operation steps
        for step_str in col_op_steps:
            parts = step_str.split(DELIM)
            self.assertGreaterEqual(len(parts), 2, f"Column op step has too few parts: {step_str}")
            col_name = parts[1]
            self.assertTrue(col_name.startswith("frac_") or col_name.startswith("int_"), f"Invalid column name format: {col_name} in step {step_str}")
            try:
                int(col_name.split('_')[1])
            except (IndexError, ValueError):
                 self.fail(f"Invalid column index in name: {col_name} in step {step_str}")


    def test_generate_addition(self):
        """Test the generate method for addition."""
        generator_add = DecimalAddSubGenerator('+')
        for _ in range(10):
            result = generator_add.generate()
            self._run_basic_checks(result, "decimal_add", "+")
            # Check for specific add column step
            has_add_col_step = any(s.startswith(f"DEC_ADD_COL{DELIM}") for s in result["steps"])
            self.assertTrue(has_add_col_step, "Missing DEC_ADD_COL step in addition")
            # Track if final carry step appears in any generated example
            if any(s.startswith(f"DEC_CARRY_FINAL{DELIM}") for s in result["steps"]):
                generator_add.has_final_carry_step_in_any = True # Use instance attr to track across loop

        # Check if at least one example generated a final carry step (probabilistic)
        self.assertTrue(getattr(generator_add, 'has_final_carry_step_in_any', False),
                        "DEC_CARRY_FINAL step was not generated in any addition test case")


    def test_generate_subtraction(self):
        """Test the generate method for subtraction."""
        generator_sub = DecimalAddSubGenerator('-')
        found_borrow_case = False
        for _ in range(20): # Increase attempts to likely find a borrow case
            result = generator_sub.generate()
            self._run_basic_checks(result, "decimal_sub", "-")
            # Check for specific sub column step
            sub_col_steps = [s for s in result["steps"] if s.startswith(f"DEC_SUB_COL{DELIM}")]
            self.assertTrue(len(sub_col_steps) > 0, "Missing DEC_SUB_COL step in subtraction")
            # Check if any step indicated a borrow occurred
            for step_str in sub_col_steps:
                if "(borrow_out 1)" in step_str:
                    found_borrow_case = True
                    # Optional: Add more specific checks here if needed for borrow visualization
                    # e.g., check the format of the 'details_str' part for borrow_in
                    # parts = step_str.split(DELIM)
                    # self.assertIn("(borrow_in 1)", parts[2], f"Borrow out implies borrow in for next step (or previous borrow): {step_str}")
                    break # Found a borrow case for this example

        self.assertTrue(found_borrow_case, "No subtraction example requiring borrowing was generated in tests.")


if __name__ == '__main__':
    unittest.main()
