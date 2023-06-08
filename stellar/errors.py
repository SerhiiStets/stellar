# TODO

class InvalidSymbol(Exception):
    def __init__(self, code, position, line_number) -> None:
        self._code = code
        self._position = position
        self._line_number = line_number

        self.message = f"InvalidSymbol '{self._code[self._position]}' on line {self._line_number}\n\
        {code.splitlines()[line_number]}"

        super().__init__(self.message)
