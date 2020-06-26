import os
import subprocess
import json
from visualizer import Visualizer
from nodes import *

from pprint import pprint #DEBUG

AST_TYPES = {
    'AnnAssign': ':',
    'Assign': '=',
    'AugAssign': {
      'Add': '+=',
      'Sub': '-=',
      'Multiply': '*=',
      'Divide': '/=',
      'Modulo': '%=',
      'And': '&=',
      'Or': '|=',
      'Xor': '^=',
      'Shiftleft': '<<=',
      'Shiftright': '>>=',
      'Exponent': '**=',
      'Integerdiv': '//='
    },
}

OPERATORS = {
  'Add': ' + ',
  'Sub': ' - ',
  'Multiply': ' * ',
  'Divide': ' / ',
  'Modulo': ' % ',
}

COMPARITORS = {
    'Lt': '\<',
    'LtE': '\<=',
    'Gt': '\>',
    'GtE': '\>=',
    'Not': 'not',
}


class AstWalker:
    def __init__(self, source: str):
        self._contract_name = '' 
        self._ast = self.__get_ast(source)

    def walk(self, node, nodes):
        if 'FunctionDef' in node['ast_type']:
            nodes.append(node)
        if "body" in node and node["body"]:
            for child in node["body"]:
                self.walk(child, nodes)

    def __get_ast(self, filename: str) -> dict:
        cmd = 'vyper -f ast {}'.format(filename)
        try:
            FNULL = open(os.devnull, 'w')
            vyper_c = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=FNULL)
            ast = json.loads(vyper_c.communicate()[0].decode('utf-8', 'strict'))
            self._contract_name = ast['contract_name']
            return ast['ast']
        except json.decoder.JSONDecodeError:
            if not os.path.isfile(filename):
                print('Error: The file "{}" does not exist'.format(filename))
            else:
                print('Error: Could not parse Vyper file: ({})'.format(filename))
                vyper_c.communicate()[0].decode('utf-8', 'strict')
            exit(1)

    def get_contract_name(self):
        return self._contract_name

    def parse_ast(self, ast: dict) -> list:
        #TODO: DELETE THIS WHEN DONE 
        body = ast['body']
        statements = [] # Empty list of Strings
        for statement in body:
            statements.append(self.parse_statements(statement))
        print(statements)
        return statements

    def parse_ast_alt(self, ast:dict) -> list:
        #TODO: Change this to just parse_ast
        body = ast['body']
        statements = [] # Empty list of Strings
        for statement in body:
            statements.append(self.__parse_statements(statement))
        main = ContractNode(self._contract_name, statements)
        return main

    def parse_statements(self, statement: dict):
        # TODO: handle AnnAssign nodes here
        # TODO: WORK TO REMVOE THIS
        ast_type = self.get_ast_type(statement)
        if ast_type == 'FunctionDef':
            body = self.__parse_body_cfg(statement['body']) # Returns a list of statements 
            decorator_list = statement['decorator_list']
            decorator_list_res = []
            for decorator in decorator_list:
                if decorator['id'] == 'public':
                    is_public = True
                elif decorator['id'] == 'private':
                    is_public = False
                decorator_list_res.append(decorator['id'])
            args = statement['args']['args']
            if statement['returns'] == None:
                returns = ''
            else:
                returns = statement['returns']['id']
            name = statement['name']
            return FunctionNode(name, body, is_public, decorator_list_res, args, returns)

    def __parse_statements(self, statement: dict):
        # TODO: handle AnnAssign nodes here
        # TODO: MAKE THIS THE BETTER PARSE_STATMEENTS FUNCTION
        ast_type = self.get_ast_type(statement)
        if ast_type == 'FunctionDef':
            body = self.__parse_body(statement['body']) # Returns a list of statements 
            decorator_list = statement['decorator_list']
            decorator_list_res = []
            for decorator in decorator_list:
                if decorator['ast_type'] == 'Name':
                    if decorator['id'] == 'public':
                        is_public = True
                    elif decorator['id'] == 'private':
                        is_public = False
                    decorator_list_res.append(decorator['id'])
                elif decorator['ast_type'] == 'Call':
                    # TODO: make sure this can get all the args for the non-rentrant decorator
                    decorator_list_res.append(decorator['func']['id']) 
                else:
                    print('ERROR: Unknown Decorator')
                    raise Exception
            args = statement['args']['args']
            if statement['returns'] == None:
                returns = ''
            else:
                returns = statement['returns']['id']
            name = statement['name']
            return FunctionNode(name, body, is_public, decorator_list_res, args, returns)
        
    def get_call_args(self, args: list) -> list:
        ret = []
        for arg in args:
            ret.append(self.__get_right(arg))
        return ret

    def __parse_body(self, body: list) -> list:
        # TODO: make it prettier (fix the slashes on the end to be on the same column)
        statement_objs = []
        for statement in body:
            ast_type = self.get_ast_type(statement)
            try:
                if ast_type == 'Assign':
                    node = BinaryOperatorNode(ast_type, self.__get_left(statement['target']), self.__get_right(statement['value']))
                    statement_objs.append(StatementNode(ast_type, AST_TYPES['Assign'], node))
                elif ast_type == 'AugAssign':
                    node = BinaryOperatorNode(ast_type, self.__get_left(statement['target']), self.__get_right(statement['value']))
                    op = self.get_op(statement) 
                    statement_objs.append(StatementNode(ast_type, AST_TYPES['AugAssign'][op],               \
                            node))
                elif ast_type == 'AnnAssign':
                    node = BinaryOperatorNode(ast_type, self.__get_left(statement['target']), self.__get_right(statement['value']))
                    statement_objs.append(StatementNode(ast_type, statement['annotation']['id'],            \
                            node))
                elif ast_type == 'Expr':
                    node = CallNode(statement['value']['func']['id'], self.get_call_args(statement['value']['args']))
                    statement_objs.append(StatementNode(ast_type, 'Call', 
                            node))
                elif ast_type == 'Assert':
                    if statement['test']['ast_type'] == 'Compare':
                        node = AssertNode(self.__get_left(statement['test']['left']), self.__get_right(statement['test']['right']))
                        statement_objs.append(StatementNode(ast_type,                                       \
                            COMPARITORS[statement['test']['op']['ast_type']],                                  \
                            node))
                    elif statement['test']['ast_type'] == 'UnaryOp':
                        node = AssertNode(self.__get_left(statement['test']['operand']), None)
                        statement_objs.append(StatementNode(ast_type,                                     \
                            COMPARITORS[statement['test']['op']['ast_type']],                                  \
                            node))
                elif ast_type == 'Return':
                    # TODO: Generalize for all constants not just Int
                    #TODO: change to nodes
                    if statement['value']['ast_type'] == "Int":
                        statement_objs.append(StatementNode(ast_type, 'return', None, statement['value']['value']))
                    else:
                        statement_objs.append(StatementNode(ast_type, 'return', None, statement['value']['attr']))
            except KeyError as e:
                pprint(statement)
                raise e
        return statement_objs

    def __parse_body_cfg(self, body: list) -> list:
        statements = []
        for statement in body:
            ast_type = self.get_ast_type(statement)
            print(ast_type) 
            try:
                if ast_type == 'Assign':
                    statements.append('{} {} {}'.format(
                            self.get_left(statement['target']), 
                            AST_TYPES['Assign'],
                            self.get_right(statement['value'])))
                elif ast_type == 'AugAssign':
                    op = self.get_op(statement) 
                    statements.append('{} {} {}'.format(
                            self.get_left(statement['target']), 
                            AST_TYPES['AugAssign'][op],
                            self.get_right(statement['value'])))
                elif ast_type == 'AnnAssign':
                    statements.append('{}:{} = {}'.format(self.get_left(statement['target']), \
                        statement['annotation']['id'],                                        \
                        self.get_right(statement['value'])))
                elif ast_type == 'Expr':
                    statements.append('{}({})'.format(statement['value']['func']['id'],                                        \
                        self.get_func_args(statement['value']['args'])))
                elif ast_type == 'Assert':
                    if statement['test']['ast_type'] == 'Compare':
                        statements.append('assert {} {} {}'.format(self.get_left(statement['test']['left']),
                            COMPARITORS[statement['test']['op']['ast_type']],
                            self.get_right(statement['test']['right'])))
                    elif statement['test']['ast_type'] == 'UnaryOp':
                        statements.append('assert {} {}'.format(COMPARITORS[statement['test']['op']['ast_type']],
                            self.get_right(statement['test']['operand'])))
                elif ast_type == 'Return':
                    statements.append('return {}'.format(statement['value']['attr']))
            except KeyError as e:
                pprint(statement)
                raise e
        print(statements)
        return statements

    def get_func_args(self, arg_list: list) -> str:
        ret = ''
        for i in range(len(arg_list) - 1):
            ret += self.get_right(arg_list[i])
            ret += ', '
        if len(arg_list) > 0:
            ret += self.get_right(arg_list[-1])
        return ret

    def get_ast_type(self, statement: dict) -> str:
        return statement['ast_type']

    def get_op(self, statement: dict) -> str:
        return statement['op']['ast_type']

    def get_aug_operator(self, ast_type: str) -> str:
        return AST_TYPES['AugAssign'][ast_type] 

    # Get left hand side of a assignment
    def get_left(self, left: dict) -> str:
        ## TODO: make get_left take statement['target]
        ast_type = left['ast_type']
        if ast_type == 'Subscript':
            return self.get_left(left['value']) +  \
                '[' + self.get_right(left['slice']['value']) + ']'
        elif ast_type == 'Attribute':
            return left['value']['id'] + '.' + left['attr']
        elif ast_type == 'Name':
            return left['id']
        #return left['attr']

    # Get left hand side of a assignment
    def __get_left(self, left: dict) -> list:
        ## TODO: make get_left take statement['target]
        ## TODO: Add BinOp
        ast_type = left['ast_type']
        if ast_type == 'Subscript':
            #return self.get_left(left['value']) +  \
            #    '[' + self.get_right(left['slice']['value']) + ']
            left_var = self.__get_left(left['value'])
            subscript = self.__get_right(left['slice']['value'])
            return SubscriptNode(left_var, ast_type, left, subscript)
        elif ast_type == 'Attribute':
            return VariableNode(left['value']['id'] + '.' + left['attr'], ast_type, left)
        elif ast_type == 'Name':
            return VariableNode(left['id'], ast_type, left)
        #return left['attr']

    # Get right hand side of an assignment
    ## TODO: Get rid of ast_type if statements
    def get_right(self, right: dict) -> str:
        ast_type = right['ast_type']
        if ast_type == 'Name':
            return right['id']
        elif ast_type == 'Attribute':
            return right['value']['id'] + '.' + right['attr'] 
        elif ast_type == 'Int':
            return right['value']
        elif ast_type == 'NameConstant':
            return right['value']
        elif ast_type == 'BinOp':
            print(ast_type)
            print(right)
            return self.get_right(right['left']) +                                              \
                OPERATORS[right['op']['ast_type']] +                                            \
                self.get_right(right['right'])
        elif ast_type == 'Subscript':
            return self.get_right(right['value']) +                                             \
                '[' + self.get_right(right['slice']['value']) + ']'

    ## TODO: Get rid of ast_type if statements
    def __get_right(self, right: dict):
        #TODO: Unary operator needs to be done
        ast_type = right['ast_type']
        if ast_type == 'Name':
            return VariableNode(right['id'], ast_type, right)
        elif ast_type == 'Attribute':
            return VariableNode(right['value']['id'] + '.' + right['attr'], ast_type, right)
        elif ast_type == 'Int':
            #return VariableNode(right['value'], ast_type, right)
            return ConstantNode(right['value'])
        elif ast_type == 'NameConstant':
            #return right['value']
            return ConstantNode(int(right['value']))
        elif ast_type == 'BinOp':
            print(ast_type)
            print(right)
            return BinaryOperatorNode(ast_type, self.__get_right(right['left']), self.__get_right(right['right']))
        elif ast_type == 'Subscript':
            return self.get_right(right['value']) +                                             \
                '[' + self.get_right(right['slice']['value']) + ']'

    def get_variable(self, line: dict, body: list):
        pass

    def get_target(self, target: dict) -> str:
        pass

    def get_value(self, value: dict) -> str:
        pass
    
    

#TODO: remove
if __name__ == '__main__':
    #ast = AstWalker('example_vyper_contracts/open_auction.vy')
    ast = AstWalker('example_vyper_contracts/vulnerable.vy')
    #ast = AstWalker('example_vyper_contracts/storage.vy')
    nodes = []
    ast.walk(ast._ast, nodes)
    #parsed_ast = visualizer.parse_ast(ast._ast)
    #visualizer.visualize_cfg(parsed_ast)
    parsed_ast = ast.parse_ast_alt(ast._ast)
    visualizer = Visualizer(ast.get_contract_name())
    visualizer.visualize_ast(parsed_ast)