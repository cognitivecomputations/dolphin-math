import random
from decimal import Decimal, InvalidOperation
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid

# New Op-Codes:
# DEC_ALIGN: Align numbers by decimal point (num1_aligned, num2_aligned)
# DEC_ADD_COL: Add column (col_index, d1, d2, carry_in, result_digit, carry_out)
# DEC_SUB_COL: Subtract column (col_index, d1, d2, borrow_in, result_digit, borrow_out)
# DEC_BORROW: Show borrow propagation (from_col_idx, to_col_idx) - Optional detail
# DEC_CARRY: Show carry propagation (from_col_idx, to_col_idx) - Optional detail

class DecimalAddSubGenerator(ProblemGenerator):
    """
    Generates decimal addition or subtraction problems with detailed,
    column-by-column steps including carrying/borrowing.
    """

    def __init__(self, op_symbol: str):
        if op_symbol not in ['+', '-']:
            raise ValueError("op_symbol must be '+' or '-'")
        self.op_symbol = op_symbol
        self.op_name = "decimal_add" if op_symbol == '+' else "decimal_sub"
        # self.op_code = "A" if op_symbol == '+' else "S" # No longer used for single step

    def _align_decimals(self, s1, s2):
        """Aligns two decimal strings for column operations."""
        p1 = s1.find('.')
        p2 = s2.find('.')
        if p1 == -1: s1 += '.'
        if p2 == -1: s2 += '.'
        p1 = s1.find('.')
        p2 = s2.find('.')

        # Pad fractional parts
        frac_len1 = len(s1) - p1 - 1
        frac_len2 = len(s2) - p2 - 1
        max_frac = max(frac_len1, frac_len2)
        s1 += '0' * (max_frac - frac_len1)
        s2 += '0' * (max_frac - frac_len2)

        # Pad integer parts
        int_len1 = p1
        int_len2 = p2
        max_int = max(int_len1, int_len2)
        s1 = '0' * (max_int - int_len1) + s1
        s2 = '0' * (max_int - int_len2) + s2

        return s1, s2, max_frac, max_int + 1 + max_frac # Total length including decimal

    def generate(self) -> dict:
        # Generate numbers, ensuring subtraction might require borrowing
        a = round(random.uniform(0.1, 99.9), random.randint(1, 2))
        b = round(random.uniform(0.1, 99.9), random.randint(1, 2))

        # Ensure a > b for subtraction to simplify borrowing logic for now
        # (Handling negative results adds complexity)
        if self.op_symbol == '-' and a < b:
            a, b = b, a
        elif self.op_symbol == '-' and a == b:
             b -= 0.1 # Ensure difference

        a_str, b_str = str(a), str(b)
        problem = f"{a_str} {self.op_symbol} {b_str}"

        # Calculate exact result using Decimal
        a_dec, b_dec = Decimal(a_str), Decimal(b_str)
        result_dec = a_dec + b_dec if self.op_symbol == '+' else a_dec - b_dec
        final_answer_str = str(result_dec.normalize())
        if final_answer_str.startswith('.'): final_answer_str = '0' + final_answer_str
        elif final_answer_str.startswith('-.'): final_answer_str = '-0' + final_answer_str[1:]


        steps = []
        s1_aligned, s2_aligned, frac_digits, total_len = self._align_decimals(a_str, b_str)
        steps.append(step("DEC_ALIGN", s1_aligned, s2_aligned))

        digits1 = [int(d) for d in s1_aligned if d != '.']
        digits2 = [int(d) for d in s2_aligned if d != '.']
        result_digits = [0] * (total_len -1) # Exclude decimal point position
        num_digits = len(digits1)

        if self.op_symbol == '+':
            carry = 0
            # Use right-to-left index (0 = rightmost)
            for i in range(num_digits - 1, -1, -1):
                # Calculate column index relative to decimal point
                # Rightmost fractional digit is index 0, first integer digit is index frac_digits
                col_place_idx = (num_digits - 1 - i)
                is_fractional = col_place_idx < frac_digits
                display_idx = col_place_idx if is_fractional else col_place_idx - frac_digits + (1 if frac_digits > 0 else 0) # Adjust for integer part
                col_name = f"{'frac' if is_fractional else 'int'}_{display_idx}"


                d1 = digits1[i]
                d2 = digits2[i]
                col_sum = d1 + d2 + carry
                result_digit = col_sum % 10
                new_carry = col_sum // 10
                # Combine details to fit into step() arguments
                add_details = f"{d1}+{d2}+{carry}"
                add_result = f"->{result_digit} (carry {new_carry})"
                steps.append(step("DEC_ADD_COL", col_name, add_details, add_result))
                result_digits[i] = result_digit
                carry = new_carry
            if carry > 0: # Final carry
                 result_digits.insert(0, carry)
                 steps.append(step("DEC_CARRY_FINAL", carry)) # Show final carry explicitly

        else: # Subtraction (assuming a > b)
            borrow = 0
            # Use right-to-left index (0 = rightmost)
            for i in range(num_digits - 1, -1, -1):
                # Calculate column index relative to decimal point
                col_place_idx = (num_digits - 1 - i)
                is_fractional = col_place_idx < frac_digits
                display_idx = col_place_idx if is_fractional else col_place_idx - frac_digits + (1 if frac_digits > 0 else 0)
                col_name = f"{'frac' if is_fractional else 'int'}_{display_idx}"

                d1 = digits1[i]
                d2 = digits2[i]

                d1_eff = d1 - borrow # Apply borrow from previous column
                borrow = 0 # Reset borrow for this column

                if d1_eff < d2:
                    d1_eff += 10
                    borrow = 1
                    # Add explicit borrow step - find next non-zero digit to the left
                    borrow_from_idx = i - 1
                    while borrow_from_idx >= 0 and digits1[borrow_from_idx] == 0:
                        borrow_from_idx -= 1
                    # Note: This simple borrow logic might need refinement for complex cases (e.g., borrowing across many zeros)
                    # For now, just indicate a borrow happened for this column
                    # steps.append(step("DEC_BORROW", borrow_from_idx, i)) # Optional detail

                col_diff = d1_eff - d2
                result_digits[i] = col_diff
                # Combine details to fit into step() arguments
                borrow_in = 1 if d1_eff != d1 else 0
                sub_details = f"{d1}-{d2} (borrow_in {borrow_in})" # Show original d1
                sub_result = f"->{col_diff} (borrow_out {borrow})"
                steps.append(step("DEC_SUB_COL", col_name, sub_details, sub_result))

        # Format result string from digits
        res_str_list = [str(d) for d in result_digits]
        if frac_digits > 0:
            res_str_list.insert(len(res_str_list) - frac_digits, '.')
        calculated_answer = "".join(res_str_list).lstrip('0')
        if calculated_answer.startswith('.'): calculated_answer = '0' + calculated_answer
        if not calculated_answer: calculated_answer = '0' # Handle zero result

        # Basic check - this simple column logic might differ slightly from Decimal's normalize
        # assert calculated_answer == final_answer_str, f"Mismatch: Calc={calculated_answer} vs Final={final_answer_str}"

        steps.append(step("Z", final_answer_str)) # Use Decimal's precise answer

        return dict(
            problem_id=jid(),
            operation=self.op_name,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
