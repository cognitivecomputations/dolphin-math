import random
from decimal import Decimal, InvalidOperation
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid

# New Op-Codes:
# MUL_SETUP: Show integer multiplication setup (int1_str, int2_str)
# MUL_PARTIAL: Multiply top int by one digit of bottom int (digit, top_int_str, partial_product_str)
# ADD_PARTIALS: Sum the (shifted) partial products (pp1_str, pp2_str, ..., sum_str)
# COUNT_DP: Count total decimal places in original factors (dp1, dp2, total_dp)
# PLACE_DP: Place decimal point in the final integer sum (sum_int_str, total_dp, final_result_str)

class DecimalMultGenerator(ProblemGenerator):
    """
    Generates decimal multiplication problems with detailed,
    long-multiplication steps.
    """

    def generate(self) -> dict:
        a = round(random.uniform(0.1, 99.9), random.randint(1, 2))
        b = round(random.uniform(0.1, 99.9), random.randint(1, 2))
        a_str, b_str = str(a), str(b)
        operation = "decimal_mul"
        problem = f"{a_str} * {b_str}"

        # Calculate exact result using Decimal for final answer
        res_decimal = Decimal(a_str) * Decimal(b_str)
        final_answer_str = str(res_decimal.normalize())
        if final_answer_str.startswith('.'): final_answer_str = '0' + final_answer_str
        elif final_answer_str.startswith('-.'): final_answer_str = '-0' + final_answer_str[1:]

        # --- Generate Steps ---
        steps = []

        # 1. Setup Integer Multiplication
        a_dp = len(a_str.split(".")[1]) if '.' in a_str else 0
        b_dp = len(b_str.split(".")[1]) if '.' in b_str else 0
        total_dp = a_dp + b_dp

        a_i_str = a_str.replace(".", "")
        b_i_str = b_str.replace(".", "")
        a_i = int(a_i_str)
        b_i = int(b_i_str)
        steps.append(step("MUL_SETUP", a_i_str, b_i_str))

        # 2. Calculate Partial Products
        partial_products = []
        shift = 0
        for digit_char in reversed(b_i_str):
            digit = int(digit_char)
            partial_prod_val = a_i * digit
            partial_prod_str = str(partial_prod_val)
            # Store the shifted value for summation later
            shifted_partial_prod_val = partial_prod_val * (10**shift)
            partial_products.append(shifted_partial_prod_val)
            # Add step showing the partial product calculation
            steps.append(step("MUL_PARTIAL", digit, a_i_str, partial_prod_str + ('0'*shift)))
            shift += 1

        # 3. Add Partial Products
        sum_val = sum(partial_products)
        sum_str = str(sum_val)
        # Combine partial products into one string for the step argument
        pp_sum_str = "+".join(str(pp) for pp in partial_products)
        steps.append(step("ADD_PARTIALS", pp_sum_str, sum_str)) # op, partial_products_sum_str, result_sum_str

        # 4. Count Decimal Places
        steps.append(step("COUNT_DP", a_dp, b_dp, total_dp))

        # 5. Place Decimal Point
        steps.append(step("PLACE_DP", sum_str, total_dp, final_answer_str))

        # 6. Final Answer Step
        steps.append(step("Z", final_answer_str))

        return dict(
            problem_id=jid(),
            operation=operation,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
