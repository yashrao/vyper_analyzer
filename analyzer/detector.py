from nodes import *

class Detector:
    def __init__(self, parsed_ast: ContractNode):
        self._parsed_ast = parsed_ast # A contract node

    def type_check(self):
        self._parsed_ast.resolve_type() # starts the chain of type checking

    def reentrancy(self):
        ## TODO: check that the @nonreentrant is used
        ## TODO: (NOT AST LEVEL) make sure implemented in IR
        pass

    # Check for delegate_call vulnerability
    def delegate_call(self):
        ## TODO: check that the @constant
        #  is used if there is a raw_call(..., delegate_call=True)
        for node in self._parsed_ast:
            if type(node) is FunctionNode:
                for statement in node.get_body():
                   pass