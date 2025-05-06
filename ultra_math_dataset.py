#!/usr/bin/env python3
# -----------------------------------------------------------
# ultra_math_dataset.py
# Main script to generate the dataset using individual generator classes.
# -----------------------------------------------------------
import json
import random
import argparse
import sys
import os

# Dynamically add the parent directory to sys.path to allow absolute imports
# when running the script directly.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import Generator Classes (from generators subdirectory)
from arithmetic.generators.long_division_generator import LongDivisionGenerator
from arithmetic.generators.decimal_mult_generator import DecimalMultGenerator
from arithmetic.generators.decimal_add_sub_generator import DecimalAddSubGenerator
from arithmetic.generators.decimal_div_generator import DecimalDivGenerator
from arithmetic.generators.fraction_op_generator import FractionOpGenerator
from arithmetic.generators.linear_simple_generator import LinearSimpleGenerator
from arithmetic.generators.quadratic_generator import QuadraticGenerator
from arithmetic.generators.simplify_expression_generator import SimplifyExpressionGenerator
from arithmetic.generators.evaluate_expression_generator import EvaluateExpressionGenerator
from arithmetic.generators.linear_complex_generator import LinearComplexGenerator
from arithmetic.generators.pythag_hyp_generator import PythagHypGenerator
from arithmetic.generators.abacus_addition_generator import AbacusAdditionGenerator
from arithmetic.generators.proportional_relationship_generator import ProportionalRelationshipGenerator
from arithmetic.generators.percent_problem_generator import PercentProblemGenerator

# Import Helpers if needed (jid is used in generate methods, step/DELIM are used internally)
# from arithmetic.helpers import jid, step, DELIM # Not strictly needed here anymore

# -----------------------------------------------------------
# definitive op-code legend (For reference across generator files)
# -----------------------------------------------------------
# Arithmetic  : D(ivide), M(ultiply), S(ubtract), A(dd)
#             : B(ring down: remainder_before, digit_down, new_num_to_divide)
#             : R(emainder)
#             : C(onvert fraction for LCD)
#             : L(CD calculation)
#             : I(nvert fraction: orig_frac_str, inverted_frac_str)
#             : PDEC(Place Decimal in product - old method)
#             : F(raction simplification)
# Dec Add/Sub : DEC_ALIGN(num1_aligned, num2_aligned)
#             : DEC_ADD_COL(col_name, details_str, result_str)
#             : DEC_SUB_COL(col_name, details_str, result_str)
#             : DEC_CARRY_FINAL(carry_digit)
# Dec Mult    : MUL_SETUP(int1_str, int2_str)
#             : MUL_PARTIAL(digit, top_int_str, partial_product_shifted_str)
#             : ADD_PARTIALS(sum_expression_str, result_sum_str)
#             : COUNT_DP(dp1, dp2, total_dp)
#             : PLACE_DP(sum_int_str, total_dp, final_result_str)
# Dec Div     : DEC_SHIFT(orig_expr, shifted_expr, shift_places)
#             : DIV_SETUP(integer_dividend, integer_divisor)
#             : PLACE_DP_Q(quotient_digits_str, dp_position_from_left_in_shifted_dividend)
#             : (Reuses B, D, M, S from Arithmetic)
# Percent     : PERCENT_TO_DEC, SETUP_PERCENT_EQ, REARRANGE_EQ, PERCENT_CALC_PART, DEC_TO_PERCENT
#             : (Uses division steps internally for find_percent/find_whole)
# Algebra     : G(CD - not used?), DISC(riminant calc), ROOT(square root)
#             : Q1/Q2(Quadratic formula roots)
#             : DIST(ribute term: factor, expr_in_parens, result_expr)
#             : REWRITE(expression/equation after step: new_form_string)
#             : COMB_X(Combine X terms: term1, term2, result_term)
#             : COMB_CONST(Combine Constant terms: const1, const2, result_const)
#             : SUBST(itute value: var_name, value, resulting_expr)
#             : MOVE_TERM(term_moved, target_side, resulting_equation_str)
#             : DIV_COEFF(Divide by coefficient: numerator, denominator, result_str)
# Geometry    : E(xponent/Power)
#             : (Reuses ROOT)
# Algebra+    : PROP_SETUP (Proportional relationships)
# Tools       : AB_SET AB_INFO AB_ADD_DGT AB_CARRY AB_CARRY_FINAL
# Final Answer: Z  (Contains the final formatted answer string)
# -----------------------------------------------------------

# Instantiate Generators
# Note: For generators requiring args (like fractions, decimal add/sub),
# we instantiate one for each variant.
ALL_GENERATORS = [
    # Basic Arithmetic
    LongDivisionGenerator(),
    DecimalMultGenerator(),
    DecimalAddSubGenerator('+'), # Add
    DecimalAddSubGenerator('-'), # Subtract
    DecimalDivGenerator(),
    FractionOpGenerator('+'),    # Add
    FractionOpGenerator('-'),    # Subtract
    FractionOpGenerator('*'),    # Multiply
    FractionOpGenerator('/'),    # Divide
    # Algebra
    LinearSimpleGenerator(),
    QuadraticGenerator(),
    SimplifyExpressionGenerator(),
    EvaluateExpressionGenerator(),
    LinearComplexGenerator(),
    ProportionalRelationshipGenerator(),
    # Geometry
    PythagHypGenerator(),
    # Tools/Methods
    AbacusAdditionGenerator(),
    # Percentages
    PercentProblemGenerator(),
]

def write_jsonl(fp, obj):
    """Writes a JSON object to a file handle, one object per line."""
    fp.write(json.dumps(obj, ensure_ascii=False) + "\n")

def build_dataset(n=10_000, path="math_visible_dataset_refactored.jsonl", seed=42):
    """Generates the dataset by calling the generate() method of chosen generators."""
    random.seed(seed)
    count = 0
    attempts = 0
    # Allow slightly more attempts in case some generators fail validation often
    max_attempts = int(n * 1.2) + 50

    print(f"Attempting to generate {n} examples...")
    # Explicitly set encoding='utf-8' for writing
    with open(path, "w", encoding="utf-8") as fp:
        while count < n and attempts < max_attempts:
            attempts += 1
            try:
                # Choose a generator instance randomly
                gen_instance = random.choice(ALL_GENERATORS)
                example = gen_instance.generate() # Call the generate method
                if example:
                    # Basic validation before writing
                    assert 'problem_id' in example
                    assert 'operation' in example
                    assert 'problem' in example
                    assert 'steps' in example and isinstance(example['steps'], list) and len(example['steps']) > 0
                    assert 'final_answer' in example
                    assert example['steps'][-1].startswith("Z|") # Check final step format

                    write_jsonl(fp, example)
                    count += 1
                    if count % 1000 == 0 and count > 0:
                        print(f"... successfully generated {count}/{n} examples")
            except Exception as e:
                # Provide more context on which generator failed
                gen_name = gen_instance.__class__.__name__ if 'gen_instance' in locals() else "Unknown"
                print(f"ERROR: Generator {gen_name} failed during generation or validation: {e}. Skipping attempt {attempts}.")
                # Optional: Add more detailed error logging or handling here

    print(f"✔  Successfully wrote {count} lines → {path} (after {attempts} attempts)")
    if count < n:
        print(f"WARN: Target of {n} examples not reached ({count}/{n}). Consider increasing max_attempts or checking generator logic.")

# ---------- Main Execution Block ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Ultra Math Dataset")
    parser.add_argument(
        "-n", "--num_examples",
        type=int,
        default=10000,
        help="Number of examples to generate."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="math_visible_dataset.jsonl",
        help="Output file path for the generated dataset."
    )
    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility."
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate one sample from each generator type instead of a full dataset."
    )

    args = parser.parse_args()

    if args.sample:
        print("Generating one sample from each generator type:")
        print("-" * 50)
        random.seed(args.seed) # Use specified or default seed

        for gen_instance in ALL_GENERATORS:
            generator_name = gen_instance.__class__.__name__
            # Handle generators that take arguments in __init__
            if hasattr(gen_instance, 'op_symbol'):
                 generator_name += f" (op='{gen_instance.op_symbol}')"

            print(f"Generator: {generator_name}")
            try:
                example = gen_instance.generate()
                print(json.dumps(example, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"  ERROR generating sample: {e}")
            print("-" * 50)
        print("Sample generation complete.")
    else:
        print(f"Generating dataset with {args.num_examples} examples...")
        build_dataset(n=args.num_examples, path=args.output, seed=args.seed)
        print("Dataset generation finished.")
