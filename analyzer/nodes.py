class ConstantNode:
    # TODO Support for multiple types
    def __init__(self, value: int):
        self._value = value

    def get_value(self):
        return self._value

    def __str__(self):
        return '<class \'ConstantNode\'; {}>'.format(self._value)

    def __repr__(self):
        return '<class \'ConstantNode\'; {}>'.format(self._value)

class BinaryOperatorNode:
    def __init__(self, ast_type:str, left, right):
        self._ast_type = ast_type
        self._left = left
        self._right = right

    def get_left(self):
        return self._left
        
    def get_right(self):
        return self._right

    def get_ast_type(self):
        return self._ast_type

class UnaryOperatorNode:
    def __init__(self, ast_type:str, var_list: list):
        self._ast_type = ast_type
        self._var_list = var_list

    def get_var_list(self):
        return self._var_list
        
    def get_ast_type(self):
        return self._ast_type
        
class VariableNode:
    def __init__(self, identifier: str, var_type: str, var_dict: dict):
        """ Used for storing individual variables in a statement """
        self._identifier = identifier
        self._var_type = var_type
        self._var_dict = var_dict

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

class SubscriptNode:
    def __init__(self, left: VariableNode, var_type: str, var_dict: dict, subscript):
        """ Used for storing individual variables in a statement """
        self._left = left
        self._var_type = var_type
        self._var_dict = var_dict
        self._subscript = subscript

    def get_left(self):
        return self._left
        
    def get_var_type(self):
        return self._var_type

    def get_var_dict(self):
        return self._var_dict
        
    def __str__(self):
        return '<class \'SubscriptNode\'; {}({}){}>'.format(self._left, self._var_type, self._subscript)

    def __repr__(self):
        return '<class \'SubscriptNode\'; {}({}){}>'.format(self._left, self._var_type, self._subscript)
        
class StatementNode:
    def __init__(self, ast_type, identifier, target, value):
        self._ast_type = ast_type
        self._identifier = identifier
        self._target = target # left
        self._value = value # right, containing either operator nodes or a single variable node
    
    def get_target(self):
        return self._target

    def get_value(self):
        return self._value

    def get_identifier(self):
        return self._identifier

    def __str__(self):
        return '<class \'StatementNode\'; {}({}), target:{}, value:{}>'.format(self._ast_type, self._identifier, self._target, self._value)

    def __repr__(self):
        return '<class \'StatementNode\'; {}({}), target:{}, value:{}>'.format(self._ast_type, self._identifier, self._target, self._value)

    ## TODO: return the re-constructed string of the entire line
    ## Useful for the CFG
    def get_line_string(self):
        return ''

class FunctionNode:
    def __init__(self, name: str, body: list, is_public: bool, decorators: list, args: list, returns: str):
        self._name = name
        self._body = body
        self._is_public = is_public
        self._decorators = decorators
        self._args = args
        self._returns = returns

    def set_name(self, name: str):
        self._name = name
    
    def get_name(self) -> str:
        return self._name
        
    def set_body(self, body: list):
        self._body = body
    
    def get_body(self) -> list:
        return self._body

    def set_is_public(self, val: bool):
        self._is_public = val

    def check_is_public(self) -> bool:
        return self._is_public
    
    def set_decorator_list(self, decorators: list):
        self._decorators = decorators

    def get_decorator_list(self) -> list:
        return self._decorators
    
    def get_arg_list(self) -> list:
        return self._args
    
    def get_returns(self) -> str:
        return self._returns
