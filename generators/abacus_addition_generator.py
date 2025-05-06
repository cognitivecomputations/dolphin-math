import random
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid

class AbacusAdditionGenerator(ProblemGenerator):
    """Generates addition problems solved using abacus-like steps."""

    def generate(self) -> dict:
        operation = "abacus_addition"
        num1 = random.randint(10, 9999)
        num2 = random.randint(10, 9999)
        result = num1 + num2
        final_answer_str = str(result)
        problem = f"{num1} + {num2}" # Neutral problem statement

        steps = []
        steps.append(step("AB_SET", num1)) # Set the first number

        s1, s2 = str(num1), str(num2)
        max_len = max(len(s1), len(s2))
        s1, s2 = s1.zfill(max_len), s2.zfill(max_len)
        # current_state = list(map(int, list(s1))) # Not actually needed for steps
        carry = 0

        steps.append(step("AB_INFO", f"Adding {num2} column by column"))

        for i in range(max_len - 1, -1, -1):
            # d1 = current_state[i] # Not needed
            d1_actual = int(s1[i]) # Get digit from original string
            d2 = int(s2[i])
            col_sum = d1_actual + d2 + carry
            # new_digit = col_sum % 10 # Not needed for steps
            new_carry = col_sum // 10

            # Combine d1, d2, carry into one string to fit the 5-arg limit for step()
            add_details = f"{d1_actual}+{d2}+{carry}"
            steps.append(step("AB_ADD_DGT", f"col_{max_len-1-i}", add_details, col_sum)) # Show column addition: col_name, details, sum

            if new_carry > 0:
                steps.append(step("AB_CARRY", f"col_{max_len-1-i}", new_carry, f"col_{max_len-i}")) # Indicate carry
                carry = new_carry
            else:
                carry = 0

        # Handle final carry if any
        if carry > 0:
            steps.append(step("AB_CARRY_FINAL", carry))

        steps.append(step("Z", final_answer_str)) # Final answer step

        return dict(
            problem_id=jid(),
            operation=operation,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
