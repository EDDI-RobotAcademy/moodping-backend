import re


class Email:

    def __init__(self, value: str):
        if not self._is_valid(value):
            raise ValueError("Invalid email format")

        self._value = value

    def __str__(self):
        return self.value

    @staticmethod
    def _is_valid(value: str) -> bool:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, value) is not None

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return isinstance(other, Email) and self.value == other.value
