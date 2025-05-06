import random
from fractions import Fraction
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid

class LinearSimpleGenerator(ProblemGenerator):
    """Generates simple linear equation problems (e.g., mx + b = y)."""

    def generate(self) -> dict:
        m = random.choice([i for i in range(-9, 10) if i != 0])
        x = random.randint(-10, 10)
        b = random.randint(-10, 10)
        y = m * x + b
        operation = "linear_eq_simple"

        rhs1 = y - b
        sol = Fraction(rhs1, m)
        final_answer_str = f"x={sol}"

        # Format problem string carefully
        lhs = f"{m:+}x".replace("+1x", "+x").replace("-1x", "-x").lstrip('+')
        if b != 0: lhs += f"{b:+d}"
        problem = f"Solve {lhs} = {y}"

        steps = [
            step("S", y, b, rhs1), # Subtract b from both sides
            step("D", rhs1, m, final_answer_str) # Divide by m
        ]
        steps.append(step("Z", final_answer_str)) # Final answer step

        return dict(
            problem_id=jid(),
            operation=operation,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
