import random
from arithmetic.base_generator import ProblemGenerator
from arithmetic.helpers import step, jid

class SimplifyExpressionGenerator(ProblemGenerator):
    """Generates algebraic expression simplification problems."""

    def generate(self) -> dict:
        operation = "simplify_expression"
        # Simplify a(bx + c) + dx + e
        a = random.choice([i for i in range(-5, 6) if i not in [0, 1]])
        b = random.choice([i for i in range(-5, 6) if i not in [0]])
        c = random.choice([i for i in range(-5, 6) if i not in [0]])
        d = random.choice([i for i in range(-5, 6) if i not in [0]])
        e = random.choice([i for i in range(-5, 6) if i not in [0]])

        # Ensure complexity: a*b + d != 0 and a*c + e != 0
        # Also ensure final expression is not just a constant or just an x term
        final_coeff_x = a * b + d
        final_const = a * c + e
        if final_coeff_x == 0 or final_const == 0:
            return self.generate() # Retry with new numbers

        problem_expr_parts = []
        # Format a(bx+c) part
        bx_c_part = f"{b}x{c:+}" if b != 1 else f"x{c:+}"
        bx_c_part = f"-x{c:+}" if b == -1 else bx_c_part
        if a == -1: problem_expr_parts.append(f"-({bx_c_part})")
        else: problem_expr_parts.append(f"{a}({bx_c_part})")

        # Format dx part
        if d != 0:
            dx_part = f"{d:+}x" if d != 1 else "+x"
            dx_part = "-x" if d == -1 else dx_part
            problem_expr_parts.append(dx_part)

        # Format e part
        if e != 0: problem_expr_parts.append(f"{e:+}")

        problem = f"Simplify: {''.join(problem_expr_parts).lstrip('+')}"

        steps = []
        # Step 1: Distribute
        dist_term1 = a * b
        dist_term2 = a * c
        dist_res_str = f"{dist_term1}x{dist_term2:+}"
        dist_res_str = dist_res_str.replace("+1x","+x").replace("-1x","-x")
        if dist_res_str.startswith("1x"): dist_res_str = "x" + dist_res_str[2:]
        elif dist_res_str.startswith("-1x"): dist_res_str = "-x" + dist_res_str[3:]
        steps.append(step("DIST", a, bx_c_part, dist_res_str))

        # Step 2: Rewrite
        rewritten_expr_parts = [dist_res_str]
        if d != 0: rewritten_expr_parts.append(dx_part)
        if e != 0: rewritten_expr_parts.append(f"{e:+}")
        rewritten_expr = "".join(rewritten_expr_parts).lstrip('+')
        steps.append(step("REWRITE", rewritten_expr))

        # Step 3: Combine x terms
        comb_x_term = f"{final_coeff_x}x".replace("1x","x").replace("-1x","-x")
        steps.append(step("COMB_X", f"{dist_term1}x", f"{d:+}x", comb_x_term))

        # Step 4: Combine constant terms
        comb_const_term = f"{final_const:+}"
        steps.append(step("COMB_CONST", f"{dist_term2:+}", f"{e:+}", comb_const_term))

        # Step 5: Final Answer
        final_answer_str = comb_x_term
        if final_const != 0: # Already includes sign
            final_answer_str += comb_const_term

        # Final cleanup if result is just 'x' or '-x'
        if final_answer_str == "1x": final_answer_str = "x"
        elif final_answer_str == "-1x": final_answer_str = "-x"

        steps.append(step("Z", final_answer_str))

        return dict(
            problem_id=jid(),
            operation=operation,
            problem=problem,
            steps=steps,
            final_answer=final_answer_str
        )
