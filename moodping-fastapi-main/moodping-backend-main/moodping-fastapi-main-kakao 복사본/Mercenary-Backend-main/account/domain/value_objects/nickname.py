class Nickname:

    def __init__(self, value: str):
        if not value or len(value) < 2:
            raise ValueError("Nickname must be at least 2 characters")
        self._value = value

    def __str__(self):
        return self.value

    @property
    def value(self):
        return self._value
