import random
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid

class ProportionalRelationshipGenerator(ProblemGenerator):
    """Generates proportional relationship problems (a/b = c/x or a/b = x/c)."""

    def generate(self) -> dict:
        operation = "proportional_relationship" # Correct operation name
        # Generate a simple proportion a/b = c/x or a/b = x/c
        # Ensure integer results for simplicity
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        k = random.randint(2, 5) # Multiplier

        if random.choice([True, False]):
            # Case 1: a/b = c/x  => x = (b*c)/a
            c = a * k
            x_ans = b * k
            problem = f"If {a} is to {b}, what is {c} proportional to?"
            proportion_str = f"{a}/{b} = {c}/x"
            cross_mult_lhs = f"{a}x"
            cross_mult_rhs_val = b * c
            cross_mult_rhs = f"{b}*{c}={cross_mult_rhs_val}" # Use * instead of ×
            division_step = f"x = {cross_mult_rhs_val}/{a}"
            divisor = a
        else:
            # Case 2: a/b = x/c => x = (a*c)/b
            c = b * k
            x_ans = a * k
            problem = f"If {a} is to {b}, what is proportional to {c}?"
            proportion_str = f"{a}/{b} = x/{c}"
            cross_mult_lhs = f"{b}x"
            cross_mult_rhs_val = a * c
            cross_mult_rhs = f"{a}*{c}={cross_mult_rhs_val}" # Use * instead of ×
            division_step = f"x = {cross_mult_rhs_val}/{b}"
            divisor = b

        final_answer_str = str(x_ans)

        steps = [
            step("PROP_SETUP", proportion_str), # Setup proportion
            step("M", cross_mult_lhs, cross_mult_rhs), # Show cross multiplication expression
            step("D", cross_mult_rhs_val, divisor, x_ans) # Show division and result (Dividend, Divisor, Quotient)
        ]
        steps.append(step("Z", final_answer_str)) # Final answer step

        return dict(
            problem_id=jid(),
            operation=operation,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
