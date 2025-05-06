import random
from fractions import Fraction
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid

class LinearComplexGenerator(ProblemGenerator):
    """Generates linear equations with variables on both sides (ax + b = cx + d)."""

    def generate(self) -> dict:
        operation = "linear_eq_complex"
        # Solve ax + b = cx + d
        a = random.choice([i for i in range(-5, 6) if i not in [0]])
        c = random.choice([i for i in range(-5, 6) if i not in [0]])
        # Ensure a != c to avoid no solution/infinite solutions
        if a == c: return self.generate() # Retry

        b = random.choice([i for i in range(-9, 10)])
        d = random.choice([i for i in range(-9, 10)])

        # Format terms carefully
        left_x = f"{a}x" if a != 1 else "x"
        left_x = "-x" if a == -1 else left_x
        left_const = f"{b:+}" if b != 0 else ""
        left_side = f"{left_x}{left_const}"

        right_x = f"{c}x" if c != 1 else "x"
        right_x = "-x" if c == -1 else right_x
        right_const = f"{d:+}" if d != 0 else ""
        right_side = f"{right_x}{right_const}".lstrip('+')
        if not right_side: right_side = "0" # Handle case cx+d = 0

        problem = f"Solve: {left_side} = {right_side}"

        steps = []
        # Step 1: Move cx term to left
        moved_cx_term_val = -c
        moved_cx_term_str = f"{moved_cx_term_val:+}x".replace("+1x","+x").replace("-1x","-x")
        new_left_side_1 = f"{left_side}{moved_cx_term_str}"
        steps.append(step("MOVE_TERM", f"{c:+}x", "left", f"{new_left_side_1} = {right_const if right_const else '0'}"))

        # Step 2: Combine x terms on left
        coeff_x = a - c
        comb_x_term = f"{coeff_x}x".replace("1x","x").replace("-1x","-x")
        # Show combination step clearly
        term_a_str = f"{a}x".replace("1x","x").replace("-1x","-x")
        term_c_str = f"{moved_cx_term_val:+}x".replace("+1x","+x").replace("-1x","-x")
        steps.append(step("COMB_X", term_a_str, term_c_str, comb_x_term))
        new_left_side_2 = f"{comb_x_term}{left_const}"
        steps.append(step("REWRITE", f"{new_left_side_2} = {right_const if right_const else '0'}"))

        # Step 3: Move b term to right
        const_val_right = d # Start with original right constant
        if b != 0:
            moved_b_term_val = -b
            moved_b_term_str = f"{moved_b_term_val:+}"
            new_right_side_1 = f"{right_const if right_const else '0'}{moved_b_term_str}"
            steps.append(step("MOVE_TERM", f"{b:+}", "right", f"{comb_x_term} = {new_right_side_1}"))

            # Step 4: Combine constant terms on right
            const_val_right = d - b
            steps.append(step("COMB_CONST", f"{d}", f"{moved_b_term_val:+}", const_val_right))
            new_right_side_2 = str(const_val_right)
            steps.append(step("REWRITE", f"{comb_x_term} = {new_right_side_2}"))
        else: # b was 0
            new_right_side_2 = str(d)

        # Step 5: Divide by coefficient
        final_val = Fraction(const_val_right, coeff_x)
        steps.append(step("DIV_COEFF", const_val_right, coeff_x, f"x={final_val}"))

        final_answer_str = f"x={final_val}"
        steps.append(step("Z", final_answer_str))

        return dict(
            problem_id=jid(),
            operation=operation,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
