from nodes import *

class Detector:
    def __init__(self, parsed_ast: ContractNode):
        self._parsed_ast = parsed_ast