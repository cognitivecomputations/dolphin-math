import random
import decimal # Required for localcontext
from decimal import Decimal, InvalidOperation
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid, DELIM

# New Op-Codes:
# DEC_SHIFT: Shift decimal points (orig_dividend, orig_divisor, new_dividend, new_divisor, shift_places)
# DIV_SETUP: Setup long division (integer_dividend, integer_divisor)
# B: Bring down digit (current_num, digit_brought_down, new_num_to_divide) - Reuse
# D: Divide step (num_to_divide, divisor, quotient_digit) - Reuse
# M: Multiply step (quotient_digit, divisor, product) - Reuse
# S: Subtract step (current_num, product, remainder) - Reuse
# R: Final Remainder (if any) - Reuse (Likely 0 for terminating decimals)
# PLACE_DP_Q: Place decimal in quotient (quotient_str_no_dp, position_from_right, final_quotient_str)

class DecimalDivGenerator(ProblemGenerator):
    """
    Generates decimal division problems with detailed,
    long-division steps after shifting decimals.
    """

    def generate(self) -> dict:
        operation = "decimal_div"
        # Ensure non-zero divisor and terminating division with limited places
        attempts = 0
        while attempts < 20: # Increase attempts for finding suitable pairs
            a = round(random.uniform(0.1, 99.9), random.randint(1, 2))
            b = round(random.uniform(0.1, 9.9), random.randint(1, 2)) # Smaller divisor range

            if b == 0: continue
            a_str, b_str = str(a), str(b)
            a_dec, b_dec = Decimal(a_str), Decimal(b_str)

            try:
                # Check for termination within reasonable precision
                with decimal.localcontext() as ctx:
                    ctx.prec = 20 # Sufficient precision for check
                    result_dec = a_dec / b_dec
                normalized_result = result_dec.normalize()
                # Limit result decimal places for simpler long division display
                if abs(normalized_result.as_tuple().exponent) > 4:
                    attempts += 1
                    continue
                # Check if divisor becomes integer easily
                b_dp = len(b_str.split(".")[1]) if '.' in b_str else 0
                if b_dp == 0: # Divisor is already integer, might be too simple? Maybe allow.
                     pass # Allow integer divisors for now
                break # Found a suitable pair
            except InvalidOperation:
                attempts += 1
                continue
        else:
            # Fallback if no good pair found
            a_str, b_str = "7.5", "1.5" # 7.5 / 1.5 = 5
            a_dec, b_dec = Decimal(a_str), Decimal(b_str)
            result_dec = a_dec / b_dec

        final_answer_str = str(result_dec.normalize())
        if final_answer_str.startswith('.'): final_answer_str = '0' + final_answer_str
        elif final_answer_str.startswith('-.'): final_answer_str = '-0' + final_answer_str[1:]

        problem = f"{a_str} / {b_str}" # Use / for consistency
        steps = []

        # 1. Shift Decimals
        a_dp = len(a_str.split(".")[1]) if '.' in a_str else 0
        b_dp = len(b_str.split(".")[1]) if '.' in b_str else 0
        shift_places = b_dp

        a_i_str = a_str.replace(".", "")
        b_i_str = b_str.replace(".", "")

        # Calculate new dividend string after shift
        if a_dp >= shift_places:
            new_a_str = a_i_str[:a_dp - shift_places + len(a_i_str) - a_dp] + '.' + a_i_str[a_dp - shift_places + len(a_i_str) - a_dp:]
        else: # Need to add trailing zeros
            new_a_str = a_i_str + '0' * (shift_places - a_dp) + '.'
        new_a_str = new_a_str.rstrip('.') # Remove trailing dot if it ended up there
        new_b_str = b_i_str # Divisor becomes integer

        # Combine args: op, originals, shifted, shift_count
        steps.append(step("DEC_SHIFT", f"{a_str}/{b_str}", f"{new_a_str}/{new_b_str}", shift_places))

        # Prepare for long division (using new_a_str as the number to divide)
        dividend_str_ld = new_a_str.replace('.', '') # Use the potentially padded number string
        divisor_ld = int(new_b_str)
        dividend_dp_pos = new_a_str.find('.')
        if dividend_dp_pos == -1: dividend_dp_pos = len(new_a_str) # Position after last digit if no decimal

        steps.append(step("DIV_SETUP", dividend_str_ld, divisor_ld))

        # 2. Perform Long Division (adapted from LongDivisionGenerator)
        rem = 0
        q_str = ""
        dividend_digits = list(dividend_str_ld)
        processed_digits = 0
        current_num_str = "" # Keep track of the number being built/remainder

        while processed_digits < len(dividend_digits) or rem > 0:
             rem_before_bringdown = rem # Store remainder from previous step

             # Determine current number being divided & digit brought down
             if processed_digits < len(dividend_digits):
                 digit = dividend_digits[processed_digits]
                 current_num_str += digit
                 cur = int(current_num_str)
                 # Show bring down step only AFTER the first division step has produced a quotient digit
                 if q_str:
                     steps.append(step("B", rem_before_bringdown, digit, cur))
             elif rem > 0: # Need to bring down '0' after decimal point
                 digit = '0'
                 current_num_str += digit # Append virtual zero
                 cur = int(current_num_str)
                 # Show bring down step only AFTER the first division step has produced a quotient digit
                 if q_str:
                     steps.append(step("B", rem_before_bringdown, digit, cur)) # Show bring down '0'
             else: # Should terminate cleanly based on generator logic
                 break

             processed_digits += 1

             if cur < divisor_ld:
                 # Only add explicit 0 to quotient if we've already started it OR passed the decimal point position
                 if q_str or processed_digits > dividend_dp_pos:
                      q_str += "0"
                      # Optionally add D step: steps.append(step("D", cur, divisor_ld, 0))
                 rem = cur # Remainder is the current number itself
                 current_num_str = str(rem) if rem > 0 else "" # Reset for next digit
                 # Check if we need more precision (add more zeros?) - limited by generator logic
                 if processed_digits >= len(dividend_digits) + 4: # Limit extra zeros added
                      break # Avoid infinite loop for non-terminating (shouldn't happen)
                 continue # Bring down next digit

             q_dig = cur // divisor_ld
             prod = q_dig * divisor_ld
             new_rem = cur - prod

             steps.append(step("D", cur, divisor_ld, q_dig))
             steps.append(step("M", q_dig, divisor_ld, prod))
             steps.append(step("S", cur, prod, new_rem))

             q_str += str(q_dig)
             rem = new_rem
             current_num_str = str(rem) if rem > 0 else "" # Reset for next digit

             # Termination condition check (if remainder is 0 and no more original digits)
             if rem == 0 and processed_digits >= len(dividend_digits):
                 break
             # Limit precision
             if len(q_str.replace('.','')) > len(dividend_str_ld) + 5: # Heuristic limit
                 break


        # 3. Place Decimal Point in Quotient
        # Position is based on original decimal point position in the *shifted* dividend (new_a_str)
        quotient_dp_pos = dividend_dp_pos # Num digits before decimal in shifted dividend

        # Add step showing where decimal point goes based on calculation
        # Args: quotient_digits_string, num_digits_before_dp_in_shifted_dividend
        if not q_str: q_str = "0" # Handle cases where quotient is 0
        steps.append(step("PLACE_DP_Q", q_str, quotient_dp_pos))

        # 4. Final Answer Step (use precisely calculated one from Decimal)
        steps.append(step("Z", final_answer_str))

        return dict(
            problem_id=jid(),
            operation=operation,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
