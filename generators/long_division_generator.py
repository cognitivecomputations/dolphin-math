import random
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid, DELIM

class LongDivisionGenerator(ProblemGenerator):
    """Generates long division problems (e.g., 1234 / 56)."""

    def generate(self) -> dict:
        dividend = random.randint(10, 9999)
        divisor = random.randint(2, 99)
        steps = []
        operation = "long_division"
        problem = f"{dividend} / {divisor}" # Use / for consistency

        if dividend < divisor:  # trivial remainder-only case
            final_answer_str = f"0 R{dividend}"
            steps.append(step("R", dividend))
        else:
            rem = 0
            q_str = ""
            dividend_str = str(dividend)
            current_num_str = "" # Keep track of the number being built/remainder

            for i, digit in enumerate(dividend_str):
                rem_before_bringdown = rem # Store remainder from previous step
                current_num_str += digit
                cur = int(current_num_str)

                # Show bring down step only AFTER the first division step has produced a quotient digit
                if q_str: # If we have already started the quotient string
                    # Args: Remainder Before, Digit Brought Down, New Number to Divide
                    steps.append(step("B", rem_before_bringdown, digit, cur))
                # Else: This is the initial part being formed (e.g., 1, then 18 for 1834/5)

                if cur < divisor:
                    # If it's the first group and less than divisor, handle initial 0 implicitly
                    # Only add explicit 0 to quotient if we've already started it
                    if q_str:
                         q_str += "0"
                         # Optionally add D step: steps.append(step("D", cur, divisor, 0))
                    rem = cur # Remainder is the current number itself
                    current_num_str = str(rem) if rem > 0 else "" # Reset for next digit
                    continue # Skip division steps, get next digit

                # cur >= divisor
                q_dig = cur // divisor
                prod = q_dig * divisor
                new_rem = cur - prod

                # Add standard long division steps
                # The first D, M, S steps implicitly cover the initial part
                steps.append(step("D", cur, divisor, q_dig))
                steps.append(step("M", q_dig, divisor, prod))
                steps.append(step("S", cur, prod, new_rem))

                q_str += str(q_dig)
                rem = new_rem
                current_num_str = str(rem) if rem > 0 else "" # Reset for next digit

            # Final remainder check (No change needed here)
            if rem > 0:
                last_op_rem = None
                if steps and steps[-1].startswith("S" + DELIM):
                    try:
                        last_op_rem = int(steps[-1].split(DELIM)[-1])
                    except ValueError:
                        pass
                # Only add R step if remainder wasn't the result of the last S step
                if last_op_rem != rem:
                    steps.append(step("R", rem)) # Remainder

            final_answer_str = f"{int(q_str)}" + (f" R{rem}" if rem > 0 else "")

        steps.append(step("Z", final_answer_str)) # Final answer step

        return dict(
            problem_id=jid(),
            operation=operation,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
