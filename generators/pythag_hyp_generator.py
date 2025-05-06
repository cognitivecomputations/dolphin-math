import random
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid

class PythagHypGenerator(ProblemGenerator):
    """Generates Pythagorean theorem problems (finding hypotenuse)."""

    def generate(self) -> dict:
        operation = "pythag_hyp"
        # Use common integer triples, scaled randomly
        triples = [(3, 4, 5), (5, 12, 13), (7, 24, 25), (8, 15, 17), (9, 40, 41)]
        a, b, c_ans = random.choice(triples)
        k = random.randint(1, 5)
        a, b, c_ans = a * k, b * k, c_ans * k

        # Randomly swap a and b for variety in problem statement
        if random.choice([True, False]):
            a, b = b, a

        problem = f"Find hypotenuse: legs {a} and {b}"

        a_sq = a * a
        b_sq = b * b
        sum_sq = a_sq + b_sq
        final_answer_str = str(c_ans)

        steps = [
            step("E", a, 2, a_sq),      # Square leg a
            step("E", b, 2, b_sq),      # Square leg b
            step("A", a_sq, b_sq, sum_sq), # Add squares
            step("ROOT", sum_sq, c_ans) # Square root of sum
        ]
        steps.append(step("Z", final_answer_str)) # Final answer step

        return dict(
            problem_id=jid(),
            operation=operation,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
