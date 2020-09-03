from nodes import *

class Detector:
    def __init__(self, parsed_ast: ContractNode):
        self._parsed_ast = parsed_ast # A contract node

    def type_check(self):
        print('Starting Type Checking')
        self._parsed_ast.resolve_type() # starts the chain of type checking
        print('Finished Type Checking')

    def reentrancy(self):
        ## TODO: check that the @nonreentrant is used
        ## TODO: (NOT AST LEVEL) 
        pass

    def public_var_warning(self):
        ## TODO: warn the user about public types
        for node in self._parsed_ast.get_body():
            if type(node) is AnnAssignmentNode:
                if type(node.get_ast_type()) is PublicType:
                    print('WARNING: public variable {}'.format(node.get_ast_type()))

    # Check for delegate_call vulnerability
    def delegate_call_check(self):
        ## TODO: check that the @constant
        #  is used if there is a raw_call(..., delegate_call=True)
        raw_call = False
        vulnerable = False
        func = None # the "problem node" 
        raw_call_node = None # the node with the raw_call
        print('Starting DelegateCall Check')
        for node in self._parsed_ast.get_body():
            if type(node) is FunctionNode:
                func = node
                for statement in node.get_body():
                    if type(statement) is StatementNode:
                        val = statement.get_value()
                        if type(val) is CallNode:
                            if val.get_call() == 'raw_call':
                                for param in val.get_param_list():
                                    if type(param) is KeywordNode:
                                        if param.get_identifier() == 'delegate_call':
                                            delegate_call_cond = param.get_value()
                                            if type(delegate_call_cond) is ConstantNode:
                                                if delegate_call_cond.get_value() == 1:
                                                    ## Raw call is True
                                                    ## Check if an @constant is being used
                                                    raw_call = True
                                                    raw_call_node = val
                if raw_call:
                    ## Checking if @view is being used
                    if 'view' not in node.get_decorator_list():
                        vulnerable = True
                        func.set_problem()
                        raw_call_node.set_problem()
                else:
                    vulnerable = False

        if vulnerable:
            print('DELEGATE CALL VULNERABILITY DETECTED AT {}'.format(func.get_loc()))
        else:
            print('NO DELEGATE CALL VULNERABILITY DETECTED')
        print('DelegateCall Check Finished')
