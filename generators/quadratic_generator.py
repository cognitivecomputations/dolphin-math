import random
import math
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid

class QuadraticGenerator(ProblemGenerator):
    """Generates quadratic equation problems (ax^2 + bx + c = 0)."""

    def generate(self) -> dict:
        operation = "quadratic_eq"
        while True: # Loop until a valid quadratic with integer roots is found
            r1, r2 = random.sample(range(-6, 7), 2) # Ensure distinct roots
            a = random.randint(1, 3)
            b = -a * (r1 + r2)
            c = a * r1 * r2

            # Calculate discriminant and check for perfect square
            disc = b*b - 4*a*c
            if disc < 0: continue # Skip non-real roots

            try:
                sqrt_disc = math.isqrt(disc)
                if sqrt_disc * sqrt_disc == disc:
                    break # Found a valid one
            except AttributeError: # Fallback for Python < 3.8
                sqrt_disc_f = math.sqrt(disc)
                if sqrt_disc_f == int(sqrt_disc_f):
                    sqrt_disc = int(sqrt_disc_f)
                    break # Found a valid one
            # If not a perfect square, loop again

        denom = 2 * a
        # Ensure roots are integers (should be guaranteed by perfect square discriminant)
        root1_num = -b + sqrt_disc
        root2_num = -b - sqrt_disc
        if root1_num % denom != 0 or root2_num % denom != 0:
             # This case should be rare if logic is correct, but retry just in case
             return self.generate()


        root1 = root1_num // denom
        root2 = root2_num // denom
        # Order roots consistently (e.g., larger first)
        root1, root2 = max(root1, root2), min(root1, root2)
        final_answer_str = f"x={root1}, x={root2}"

        # Formatting logic to use ^2 instead of ²
        expr_terms = []
        if a == 1: expr_terms.append("x^2")
        elif a == -1: expr_terms.append("-x^2")
        else: expr_terms.append(f"{a}x^2")

        if b != 0:
            sign = "+" if b > 0 else "-"
            b_val_str = "" if abs(b) == 1 else str(abs(b))
            expr_terms.append(f"{sign}{b_val_str}x")
        if c != 0:
            sign = "+" if c > 0 else "" # Use sign only, value included
            expr_terms.append(f"{sign}{c}")

        expr = "".join(expr_terms).lstrip('+')
        problem = f"Solve {expr} = 0"

        steps = [
            step("DISC", b*b, 4*a*c, disc), # Calculate discriminant parts
            step("ROOT", disc, sqrt_disc), # Square root of discriminant
            step("Q1", -b, sqrt_disc, denom, root1), # Calculate first root
            step("Q2", -b, sqrt_disc, denom, root2), # Calculate second root
        ]
        steps.append(step("Z", final_answer_str)) # Final answer step

        return dict(
            problem_id=jid(),
            operation=operation,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
