"""
loc: location of the node in the source code (col_offset, end_col_offset, line_no)
"""


class Node:
    def __init__(self, ast_type: str, loc: tuple):
        self._ast_type = ast_type
        self._problem = None
        self._loc = loc

    def __str__(self):
        return '<class \'Node\';>'

    def __repr(self):
        return '<class \'Node\';>'

    def get_ast_type(self) -> str:
        return self._ast_type

    def resolve_type(self):
        print('Resolving Node')
        print('Done Node')


class ConstantNode:
    # TODO Support for multiple types
    def __init__(self, value: int, loc: tuple):
        self._value = value
        self._loc = loc

    def get_value(self) -> int:
        return self._value

    def __str__(self) -> str:
        return '<class \'ConstantNode\'; {}>'.format(self._value)

    def __repr__(self) -> str:
        return '<class \'ConstantNode\'; {}>'.format(self._value)

    def resolve_type(self):
        pass


class BinaryOperatorNode:
    def __init__(self, ast_type: str, op: str, left, right, loc: tuple):
        self._ast_type = ast_type
        self._op = op
        self._left = left
        self._right = right
        self._problem = None
        self._loc = loc

    def get_left(self):
        return self._left

    def get_right(self):
        return self._right

    def get_ast_type(self):
        return self._ast_type

    def get_op(self):
        return self._op

    def __str__(self) -> str:
        return '<class \'BinaryOpNode\'({}); {} {} {}>'.format(self._ast_type, self._left, self._op, self._right)

    def __repr__(self) -> str:
        return '<class \'BinaryOpNode\'({}); {} {} {}>'.format(self._ast_type, self._left, self._op, self._right)

    def resolve_type(self):
        print('Resolving BinaryOperatorNode')
        left = self._left.resolve_type()
        right = self._right.resolve_type()
        print(self._left)
        print(self._right)
        if left != right:
            print('Error: TypeError')
            exit(1)
        print('Done BinaryOperatorNode')


class AssignmentNode:
    def __init__(self, ast_type: str, left, right, loc: tuple):
        self._ast_type = ast_type
        self._left = left
        self._right = right
        self._problem = None
        self._loc = loc

    def get_left(self):
        return self._left

    def get_right(self):
        return self._right

    def get_ast_type(self):
        return self._ast_type

    def __str__(self) -> str:
        return '<class \'AssignmentNode\'; {} {} {}>'.format(self._ast_type, self._left, self._right)

    def __repr__(self) -> str:
        return '<class \'AssignmentNode\'; {} {} {}>'.format(self._ast_type, self._left, self._right)

    def resolve_type(self):
        print('Resolving AssignmentNode')
        self._left.resolve_type()
        self._right.resolve_type()
        print('Done AssignmentNode')


class AnnAssignmentNode:
    def __init__(self, ast_type, var_type, left, right, loc: tuple):
        self._ast_type = ast_type
        self._var_type = var_type
        self._left = left
        self._right = right
        self._problem = None
        self._loc = loc

    def get_ast_type(self):
        return self._var_type

    def __str__(self) -> str:
        return '<class \'AnnAssignmentNode\'(); {} {} {}>'.format(self._ast_type, self._left, self._right)

    def __repr__(self) -> str:
        return '<class \'AnnAssignmentNode\'(); {} {} {}>'.format(self._ast_type, self._left, self._right)

    def resolve_type(self):
        print('Resolving AnnAssignmentNode')
        self._left.resolve_type()
        if self._right != None:
            self._right.resolve_type()
        print('Done AnnAssignmentNode')


class UnaryOperatorNode:
    def __init__(self, ast_type: str, var_list: list, loc: tuple):
        self._ast_type = ast_type
        self._var_list = var_list
        self._problem = None
        self._loc = loc

    def get_var_list(self):
        return self._var_list

    def get_ast_type(self):
        return self._ast_type

    def resolve_type(self):
        print('Resolving UnaryOperatorNode')
        print('Done UnaryOperatorNode')


class CallNode:
    def __init__(self, call: str, param_list: list, loc: tuple):
        self._call = call
        self._param_list = param_list
        self._problem = None
        self._loc = loc

    def set_problem(self):
        self._problem = True

    def is_problem(self) -> bool:
        return self._problem

    def get_loc(self) -> tuple:
        return self._loc

    def get_call(self):
        return self._call

    def get_param_list(self):
        return self._param_list

    def __str__(self):
        return '<class \'CallNode\'; {}({})>'.format(self._call, self._param_list)

    def resolve_type(self):
        print('Resolving CallNode')
        print('Done CallNode')


class AssertNode:
    # TODO: Use Binary node?
    def __init__(self, left, right, comparitor: str, loc):
        self._left = left
        self._right = right
        self._comparitor = comparitor
        self._problem = None
        self._loc = loc

    def get_left(self):
        return self._left

    def get_right(self):
        return self._right

    def get_comparitor(self) -> str:
        return self._comparitor

    def __str__(self):
        return '<class \'Assert Node\'; {} ({} {})>'.format(self._comparitor, self._left, self._right)

    def __repr__(self):
        return '<class \'Assert Node\'; {} ({} {})>'.format(self._comparitor, self._left, self._right)

    def resolve_type(self):
        print('Resolving AssertNode')
        self._left.resolve_type()
        if self._right is not None:
            # Two things to compare 
            self._right.resolve_type()
        else:
            # One thing to compare
            # TODO: check if it's boolean
            pass
        print('Done AssertNode')


class VariableNode:
    def __init__(self, identifier: str, var_type: str, var_dict: dict, loc):
        """ Used for storing individual variables in a statement """
        self._identifier = identifier
        self._var_type = var_type
        self._var_dict = var_dict
        self._problem = None
        self._loc = loc
        self._is_state_variable = False

    def set_state_variable(self, state: bool):
        self._is_state_variable = state

    def is_state_variable(self) -> bool:
        return self._is_state_variable

    def get_identifier(self):
        return self._identifier

    def get_var_type(self):
        return self._var_type

    def get_var_dict(self):
        return self._var_dict

    def __str__(self):
        return '<class \'VariableNode\'; {}:{}>'.format(self._identifier, self._var_type)

    def __repr__(self):
        return '<class \'VariableNode\'; {}:{}>'.format(self._identifier, self._var_type)

    def resolve_type(self):
        return self._var_type


class KeywordNode:
    def __init__(self, identifier: str, var_type: str, value, loc):
        """ Used for storing keyword args used in method calls """
        self._identifier = identifier
        self._var_type = var_type
        self._value = value
        self._problem = None
        self._loc = loc

    def get_identifier(self):
        return self._identifier

    def get_var_type(self):
        return self._var_type

    def get_value(self):
        return self._value

    def __str__(self):
        return '<class \'KeywordNode\'; {}:{}>'.format(self._identifier, self._var_type)

    def __repr__(self):
        return '<class \'KeywordNode\'; {}:{}>'.format(self._identifier, self._var_type)

    def resolve_type(self):
        print('Resolving VariableNode')
        print('Done VariableNode')


class SubscriptNode:
    def __init__(self, left: VariableNode, var_type: str, var_dict: dict, subscript, loc):
        """ Used for storing individual variables in a statement """
        self._left = left
        self._var_type = var_type
        self._var_dict = var_dict
        self._subscript = subscript
        self._problem = None
        self._loc = loc
        self._is_state_variable = False  # True if it's a state variable

    def set_state_variable(self, state: bool):
        self._is_state_variable = state

    def is_state_variable(self) -> bool:
        return self._is_state_variable

    def get_left(self):
        return self._left

    def get_var_type(self) -> str:
        return self._var_type

    def get_var_dict(self) -> dict:
        return self._var_dict

    def get_subscript(self):
        return self._subscript

    def __str__(self):
        return '<class \'SubscriptNode\'; {}({})[{}]>'.format(self._left, self._var_type, self._subscript)

    def __repr__(self):
        return '<class \'SubscriptNode\'; {}({})[{}]>'.format(self._left, self._var_type, self._subscript)

    def resolve_type(self):
        print('Resolving SubscriptNode')
        print('Done Subscript Node')


class ReturnNode:
    def __init__(self, ast_type, identifier, value, loc):
        self._ast_type = ast_type
        self._identifier = identifier
        self._value = value
        self._loc = loc

    def get_value(self):
        return self._value

    def get_identifier(self) -> str:
        return self._identifier

    def __str__(self):
        return '<class \'ReturnNode\'; {}({}), Node:{}>'.format(self._ast_type, self._identifier, self._value)

    def __repr__(self):
        return '<class \'ReturnNode\'; {}({}), Node:{}>'.format(self._ast_type, self._identifier, self._value)

    def resolve_type(self):
        print('Resolving ReturnNode')
        print('Done ReturnNode')


class IfStatementNode:
    def __init__(self, left, right, test, body, orelse, loc):
        self._left = left
        self._right = right
        self._test = test
        self._body = body
        self._orelse = orelse
        self._loc = loc

    def get_body(self):
        return self._body

    def get_left(self):
        return self._left

    def get_right(self):
        return self._right

    def get_test(self):
        return self._test

    def get_orelse(self):
        return self._orelse

    def __str__(self):
        return '<class \'IfStatementNode\'; if({}op{}): {} else:{}>'.format(self._left, self._right, self._body, self._orelse)

    def __repr__(self):
        return '<class \'IfStatementNode\'; if({}op{})> {} else:{}>'.format(self._left, self._right, self._body, self._orelse)


class StatementNode:
    def __init__(self, ast_type, identifier, value, loc):
        self._ast_type = ast_type
        self._identifier = identifier
        self._value = value # Node containing everything 
        self._problem = None
        self._loc = loc
    
    def get_value(self):
        return self._value

    def get_identifier(self) -> str:
        return self._identifier

    def __str__(self):
        return '<class \'StatementNode\'; {}({}), Node:{}>'.format(self._ast_type, self._identifier, self._value)

    def __repr__(self):
        return '<class \'StatementNode\'; {}({}), Node:{}>'.format(self._ast_type, self._identifier, self._value)

    ## TODO: return the re-constructed string of the entire line
    ## Useful for the CFG
    def get_line_string(self) -> str:
        return ''

    def resolve_type(self):
        print('Resolving StatementNode')
        print('Done StatementNode')

class ContractNode:
    def __init__(self, name: str, body: list, src_str: str):
        self._name = name
        self._body = body
        self._symbol_table = {} # an empty dictionary for a symbol table
        self._problem = None
        self._src_str = src_str

    def get_contract_name(self) -> str:
        return self._name

    def get_body(self) -> list:
        return self._body

    def get_symbol_table(self) -> dict:
        return self._symbol_table

    def __str__(self):
        return '<class \'ContractNode\'; {}\n\t{}>'.format(self._name, self._body)

    def __repr__(self):
        return '<class \'ContractNode\'; {}\n\t{}>'.format(self._name, self._body)

    def resolve_type(self):
        print('Resolving ContractNode')
        for statement in self._body:
            statement.resolve_type()
        print('Done ContractNode')

class FunctionNode:
    def __init__(self, name: str, body: list, is_external: bool, decorators: list, args: list, returns: str, loc):
        self._name = name
        self._body = body
        self._is_external = is_external
        self._decorators = decorators
        self._args = args
        self._returns = returns
        self._symbol_table = {} # an empty dictionary for a symbol table
        self._problem = None
        self._loc = loc

    def set_problem(self):
        self._problem = True

    def get_loc(self) -> tuple:
        return self._loc

    def is_problem(self) -> bool:
        return self._problem

    def set_name(self, name: str):
        self._name = name
    
    def get_name(self) -> str:
        return self._name
        
    def set_body(self, body: list):
        self._body = body
    
    def get_body(self) -> list:
        return self._body

    def set_is_external(self, val: bool):
        self._is_external = val

    def check_is_external(self) -> bool:
        return self._is_external
    
    def set_decorator_list(self, decorators: list):
        self._decorators = decorators

    def get_decorator_list(self) -> list:
        return self._decorators
    
    def get_arg_list(self) -> list:
        return self._args
    
    def get_returns(self) -> str:
        return self._returns

    def __str__(self):
        ret = '' 
        for statement in self._body:
            ret += str(statement) + '\n'
        return '\n\t<class \'FunctionNode\'; {}\n\t\t{}>'.format(self._name, ret)

    def __repr__(self):
        ret = '' 
        for statement in self._body:
            ret += str(statement) + '\n'
        return '\n\t<class \'FunctionNode\'; {}\n\t\t{}>'.format(self._name, ret)

    def resolve_type(self):
        print('Resolving FunctionNode')
        # TODO: Check the function return and arg types 
        for statement in self._body:
            statement.resolve_type()
        print('Done FunctionNode')

class ArrayType:
    def __init__(self, ast_type: str, index: int):
        self._type = ast_type
        self._index = index
        self._problem = None

class PublicType:
    def __init__(self, ast_type: str):
        self._ast_type = ast_type

    def __str__(self) -> str:
        return '<Type \'Public\'; {}>'.format(self._ast_type)

    def __repr__(self) -> str:
        return '<Type \'Public\'; {}>'.format(self._ast_type)
