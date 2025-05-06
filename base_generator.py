from abc import ABC, abstractmethod

class ProblemGenerator(ABC):
    """Abstract base class for math problem generators."""

    @abstractmethod
    def generate(self) -> dict:
        """
        Generates a math problem instance.

        Returns:
            dict: A dictionary containing:
                - 'operation': str (e.g., 'long_division')
                - 'problem': str (e.g., '123 / 4')
                - 'final_answer': str (e.g., '30 R3')
                - 'steps': list[tuple] (e.g., [('D', 12, 4, 3), ('M', 3, 4, 12), ...])
                       Each tuple represents a step: (op_code, arg1, arg2, ...)
                       The 'Z' step tuple should be included here as the last element.
        """
        pass
