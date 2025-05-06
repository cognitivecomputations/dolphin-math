# Ultra Math Dataset Generator

## Purpose

This project generates synthetic math problems covering various arithmetic and algebra topics. Crucially, it also generates detailed, step-by-step solutions intended to mimic the process a human would follow when solving the problem manually (like a "visible scratchpad").

The output is designed for training language models to perform multi-step mathematical reasoning.

## Features

Generates problems and detailed steps for the following types:

*   **Basic Arithmetic:**
    *   Long Division (with remainder)
    *   Decimal Multiplication
    *   Decimal Addition
    *   Decimal Subtraction
    *   Decimal Division
    *   Fraction Addition (common and uncommon denominators)
    *   Fraction Subtraction (common and uncommon denominators)
    *   Fraction Multiplication
    *   Fraction Division
*   **Algebra:**
    *   Simple Linear Equations (e.g., `ax + b = c`)
    *   Complex Linear Equations (e.g., `ax + b = cx + d`)
    *   Quadratic Equations (using the quadratic formula)
    *   Simplifying Algebraic Expressions (with distribution)
    *   Evaluating Algebraic Expressions (substituting variable values)
    *   Proportional Relationships
*   **Geometry:**
    *   Pythagorean Theorem (finding hypotenuse)
*   **Percentages:**
    *   Finding the part (e.g., "What is 25% of 80?")
    *   Finding the percent (e.g., "15 is what percent of 50?")
    *   Finding the whole (e.g., "20 is 50% of what number?")
*   **Tools/Methods:**
    *   Abacus-style Addition (column-by-column with carries)

## Usage

### Generating Samples

```bash
python ultra_math_dataset.py
```

### Generating a Dataset

To generate a full dataset file (e.g., 10,000 examples) in JSON Lines format:

1.  Modify the `build_dataset()` function call within the `if __name__ == "__main__":` block in `ultra_math_dataset.py` (or call it from another script).
2.  Example call: `build_dataset(n=10000, path='my_dataset.jsonl')`
3.  Run the script: `python ultra_math_dataset.py` (if modified) or your custom script.

### Running Tests

```bash
python -m unittest discover tests
```

## Op-Code Legend

The `steps` field in the output JSON contains a list of strings, each representing a step in the solution. Steps are formatted as `OP_CODE|arg1|arg2|...`.

*   **Arithmetic:**
    *   `D`: Divide (dividend, divisor, quotient_digit)
    *   `M`: Multiply (factor1, factor2, product)
    *   `S`: Subtract (minuend, subtrahend, difference)
    *   `A`: Add (addend1, addend2, sum)
    *   `B`: Bring down (remainder_before, digit_down, new_num_to_divide)
    *   `R`: Remainder (final_remainder)
    *   `C`: Convert fraction for LCD (orig_frac_str, lcd, converted_frac_str)
    *   `L`: LCD calculation (denominator1, denominator2, lcd)
    *   `I`: Invert fraction (orig_frac_str, inverted_frac_str)
    *   `F`: Fraction simplification (unsimplified_frac_str, simplified_frac_str)
*   **Decimal Add/Sub:**
    *   `DEC_ALIGN`: Align numbers by decimal point (num1_aligned, num2_aligned)
    *   `DEC_ADD_COL`: Add column (col_name, details_str, result_str)
    *   `DEC_SUB_COL`: Subtract column (col_name, details_str, result_str)
    *   `DEC_CARRY_FINAL`: Final carry digit from leftmost column (carry_digit)
*   **Decimal Multiplication:**
    *   `MUL_SETUP`: Setup integer multiplication (int1_str, int2_str)
    *   `MUL_PARTIAL`: Multiply by digit for partial product (digit, top_int_str, partial_product_shifted_str)
    *   `ADD_PARTIALS`: Sum the partial products (sum_expression_str, result_sum_str)
    *   `COUNT_DP`: Count total decimal places in original factors (dp1, dp2, total_dp)
    *   `PLACE_DP`: Place decimal point in the final integer sum (sum_int_str, total_dp, final_result_str)
*   **Decimal Division:**
    *   `DEC_SHIFT`: Shift decimal points (orig_expr, shifted_expr, shift_places)
    *   `DIV_SETUP`: Setup long division (integer_dividend, integer_divisor)
    *   `PLACE_DP_Q`: Place decimal in quotient (quotient_digits_str, dp_position_from_left_in_shifted_dividend)
    *   *(Reuses B, D, M, S from Arithmetic)*
*   **Percentages:**
    *   `PERCENT_TO_DEC`: Convert percent to decimal (percent_str, decimal_val)
    *   `SETUP_PERCENT_EQ`: Show the equation setup (equation_str)
    *   `REARRANGE_EQ`: Show rearranged equation (rearranged_equation_str)
    *   `PERCENT_CALC_PART`: Calculate the part (percent_dec, whole, part_result) - *Only for find_part*
    *   `DEC_TO_PERCENT`: Convert decimal result back to percent (decimal_val, percent_str) - *Only for find_percent*
    *   *(Uses division steps internally for find_percent/find_whole)*
*   **Algebra:**
    *   `DISC`: Discriminant calculation (b_squared, four_ac, discriminant)
    *   `ROOT`: Square root calculation (number, root)
    *   `Q1`/`Q2`: Quadratic formula roots (neg_b, sqrt_disc, two_a, root_value)
    *   `DIST`: Distribute term (factor, expr_in_parens, result_expr)
    *   `REWRITE`: Rewrite expression/equation after step (new_form_string)
    *   `COMB_X`: Combine X terms (term1, term2, result_term)
    *   `COMB_CONST`: Combine Constant terms (const1, const2, result_const)
    *   `SUBST`: Substitute value (var_name, value, resulting_expr)
    *   `MOVE_TERM`: Move term across equals sign (term_moved, target_side, resulting_equation_str)
    *   `DIV_COEFF`: Divide by coefficient (numerator, denominator, result_str)
*   **Geometry:**
    *   `E`: Exponent/Power (base, exponent, result)
    *   *(Reuses ROOT)*
*   **Algebra+:**
    *   `PROP_SETUP`: Setup proportion (proportion_str)
*   **Tools/Methods (Abacus):**
    *   `AB_SET`: Set initial number (number)
    *   `AB_INFO`: Informational text (text)
    *   `AB_ADD_DGT`: Add digits in a column (col_name, details_str, column_sum)
    *   `AB_CARRY`: Show carry propagation (from_col, carry_value, to_col)
    *   `AB_CARRY_FINAL`: Final carry from leftmost column (carry_value)
*   **Final Answer:**
    *   `Z`: Contains the final formatted answer string (final_answer_str)

## Dependencies

*   Python 3 (tested with 3.9+)
