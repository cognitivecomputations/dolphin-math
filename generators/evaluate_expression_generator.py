import random
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid

class EvaluateExpressionGenerator(ProblemGenerator):
    """Generates algebraic expression evaluation problems."""

    def generate(self) -> dict:
        operation = "evaluate_expression"
        # Evaluate ax + by + c for x=val_x, y=val_y
        a = random.choice([i for i in range(-5, 6) if i not in [0]])
        b = random.choice([i for i in range(-5, 6) if i not in [0]])
        c = random.choice([i for i in range(-9, 10)])
        val_x = random.choice([i for i in range(-5, 6)])
        val_y = random.choice([i for i in range(-5, 6)])

        expr_parts = []
        # Format ax part
        if a == 1: expr_parts.append("x")
        elif a == -1: expr_parts.append("-x")
        else: expr_parts.append(f"{a}x")

        # Format by part
        if b == 1: expr_parts.append(f"+y")
        elif b == -1: expr_parts.append(f"-y")
        else: expr_parts.append(f"{b:+}y")

        # Format c part
        if c != 0: expr_parts.append(f"{c:+}")

        expression_str = "".join(expr_parts).lstrip('+')
        problem = f"Evaluate {expression_str} for x={val_x}, y={val_y}"

        steps = []
        # Step 1: Substitute x
        term1_val = a * val_x
        # Careful substitution to handle single 'x' and coefficient 'x'
        subst_x_expr = expression_str
        if a == 1: subst_x_expr = subst_x_expr.replace("x", f"({val_x})", 1)
        elif a == -1: subst_x_expr = subst_x_expr.replace("-x", f"-({val_x})", 1)
        else: subst_x_expr = subst_x_expr.replace(f"{a}x", f"{a}({val_x})", 1)
        steps.append(step("SUBST", "x", val_x, subst_x_expr))
        steps.append(step("M", a, val_x, term1_val)) # Calculate term with x

        # Step 2: Substitute y
        term2_val = b * val_y
        # Substitute y into the expression *after* x was substituted (subst_x_expr)
        subst_y_expr_intermediate = subst_x_expr
        if b == 1: subst_y_expr_intermediate = subst_y_expr_intermediate.replace("+y", f"+({val_y})", 1)
        elif b == -1: subst_y_expr_intermediate = subst_y_expr_intermediate.replace("-y", f"-({val_y})", 1)
        else: subst_y_expr_intermediate = subst_y_expr_intermediate.replace(f"{b:+}y", f"{b:+}({val_y})", 1)
        steps.append(step("SUBST", "y", val_y, subst_y_expr_intermediate))
        steps.append(step("M", b, val_y, term2_val)) # Calculate term with y

        # Step 3: Rewrite with calculated terms
        rewritten_expr_parts = [str(term1_val)]
        if term2_val != 0: rewritten_expr_parts.append(f"{term2_val:+}")
        if c != 0: rewritten_expr_parts.append(f"{c:+}")
        rewritten_expr = "".join(rewritten_expr_parts).lstrip('+')
        # Handle case where result is just a single number
        if not rewritten_expr: rewritten_expr = "0"
        steps.append(step("REWRITE", rewritten_expr))

        # Step 4: Calculate final sum
        final_answer_val = term1_val + term2_val + c
        # Show addition steps
        current_sum = term1_val
        if term2_val != 0:
            next_sum = current_sum + term2_val
            steps.append(step("A", current_sum, term2_val, next_sum))
            current_sum = next_sum
        if c != 0:
            next_sum = current_sum + c
            steps.append(step("A", current_sum, c, next_sum))
            current_sum = next_sum

        # Ensure final answer matches calculated sum
        assert current_sum == final_answer_val

        final_answer_str = str(final_answer_val)
        steps.append(step("Z", final_answer_str))

        return dict(
            problem_id=jid(),
            operation=operation,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
