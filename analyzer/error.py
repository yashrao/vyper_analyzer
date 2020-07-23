class TypeProblem:
    def __init__(self, message: str):
        self._message = message

    def get_message(self) -> str:
        return self._message

    def __str__(self) -> str:
        return '<Class TypeProblem; {}>'.format(self._message)

    def __repr__(self) -> str:
        return '<Class TypeProblem; {}>'.format(self._message)

class Vulnerable:
    def __init__(self, message: str):
        self._message = message

    def get_message(self) -> str:
        return self._message

    def __str__(self) -> str: 
        return '<Class Vulnerable; {}>'.format(self._message)

    def __repr__(self) -> str: 
        return '<Class Vulnerable; {}>'.format(self._message)