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
        self._ast = self.get_ast(source)

    def walk(self, node, nodes):
        if 'FunctionDef' in node['ast_type']:
            nodes.append(node)
        if "body" in node and node["body"]:
            for child in node["body"]:
                self.walk(child, nodes)

    def get_ast(self, filename: str) -> dict:
        cmd = 'vyper -f ast {}'.format(filename)
        try:
            FNULL = open(os.devnull, 'w')
            vyper_c = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

    def parse_ast(self, ast:dict) -> list:
        #TODO: Change this to just parse_ast
        body = ast['body']
        statements = [] # Empty list of Strings
        for statement in body:
            statements.append(self.parse_statements(statement))
        main = ContractNode(self._contract_name, statements)
        return main

    def parse_statements(self, statement: dict):
        # TODO: handle AnnAssign nodes here
        # TODO: MAKE THIS THE BETTER PARSE_STATMEENTS FUNCTION
        ast_type = self.get_ast_type(statement)
        if ast_type == 'FunctionDef':
            body = self.parse_body(statement['body']) # Returns a list of statements 
            decorator_list = statement['decorator_list']
            decorator_list_res = []
            for decorator in decorator_list:
                if decorator['ast_type'] == 'Name':
                    if decorator['id'] == 'external':
                        is_external = True
                    elif decorator['id'] == 'internal':
                        is_external = False
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
            return FunctionNode(name, body, is_external, decorator_list_res, args, returns)
        elif ast_type == 'AnnAssign':
            var_type = statement['annotation'] # TODO: turn into a node
            return AnnAssignmentNode(ast_type, var_type, self.get_left(statement['target']), self.get_right(statement['annotation']))
        
        
    def get_call_args(self, args: list, keywords=None) -> list:
        ret = []
        for arg in args:
            ret.append(self.get_right(arg))
        if keywords is not None:
            for keyword in keywords:
                ret.append(self.get_keyword(keyword))
        return ret

    def get_annotation(self, annotation: dict):
       return '' 

    def parse_body(self, body: list) -> list:
        # TODO: make it prettier (fix the slashes on the end to be on the same column)
        statement_objs = []
        for statement in body:
            ast_type = self.get_ast_type(statement)
            try:
                if ast_type == 'Assign':
                    node = AssignmentNode(ast_type, self.get_left(statement['target']), self.get_right(statement['value']))
                    statement_objs.append(node)
                elif ast_type == 'AugAssign':
                    op = self.get_op(statement) 
                    node = BinaryOperatorNode(ast_type, op, self.get_left(statement['target']), self.get_right(statement['value']))
                    statement_objs.append(node)
                elif ast_type == 'AnnAssign':
                    if statement['annotation']['ast_type'] != 'Subscript':
                        var_type = statement['annotation']['id']  #TODO: change to a node
                    else:
                        var_type = ArrayType(self.get_left(statement['value']),                        \
                                            statement['annotation']['slice']['value'])
                    node = AnnAssignmentNode(ast_type, var_type, self.get_left(statement['target']), self.get_right(statement['value']))
                    statement_objs.append(StatementNode(ast_type, var_type, node))
                elif ast_type == 'Expr':
                    if 'keywords' in list(statement['value'].keys()):
                        node = CallNode(statement['value']['func']['id'],                               \
                            self.get_call_args(statement['value']['args'], statement['value']['keywords']))
                    else:
                        node = CallNode(statement['value']['func']['id'], self.get_call_args(statement['value']['args']))
                    statement_objs.append(StatementNode(ast_type, 'Call', 
                            node))
                elif ast_type == 'Assert':
                    if statement['test']['ast_type'] == 'Compare':
                        node = AssertNode(self.get_left(statement['test']['left']), 
                            self.get_right(statement['test']['right']),                                \
                            COMPARITORS[statement['test']['op']['ast_type']])
                        statement_objs.append(node)
                    elif statement['test']['ast_type'] == 'UnaryOp':
                        #TODO: add the COMPARITOR thing to the assert
                        node = AssertNode(self.get_left(statement['test']['operand']), 
                            None,
                            COMPARITORS[statement['test']['op']['ast_type']])
                        statement_objs.append(node)
                elif ast_type == 'Return':
                    # TODO: Generalize for all constants not just Int
                    #TODO: change to nodes
                    if statement['value']['ast_type'] == "Int":
                        statement_objs.append(StatementNode(ast_type, 'return', statement['value']['value']))
                    else:
                        statement_objs.append(StatementNode(ast_type, 'return', statement['value']['attr']))
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
    def get_left(self, left: dict) -> list:
        ## TODO: make get_left take statement['target]
        ## TODO: Add BinOp
        ast_type = left['ast_type']
        if ast_type == 'Subscript':
            #return self.get_left(left['value']) +  \
            #    '[' + self.get_right(left['slice']['value']) + ']
            left_var = self.get_left(left['value'])
            subscript = self.get_right(left['slice']['value'])
            return SubscriptNode(left_var, ast_type, left, subscript)
        elif ast_type == 'Attribute':
            return VariableNode(left['value']['id'] + '.' + left['attr'], ast_type, left)
        elif ast_type == 'Name':
            return VariableNode(left['id'], ast_type, left)
        #return left['attr']

    ## TODO: Get rid of ast_type if statements
    def get_right(self, right: dict):
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
            op = self.get_op(right) 
            return BinaryOperatorNode(ast_type, op, self.get_right(right['left']), self.get_right(right['right']))
        elif ast_type == 'Subscript':
            left_var = self.get_left(right['value'])
            subscript = self.get_right(right['slice']['value'])
            return SubscriptNode(left_var, ast_type, right, subscript)
        
    def get_keyword(self, keyword: dict):
        return KeywordNode(keyword['arg'], keyword['value']['ast_type'], self.get_right(keyword['value']))

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
    parsed_ast = ast.parse_ast(ast._ast)
    visualizer = Visualizer(ast.get_contract_name())
    visualizer.visualize_ast(parsed_ast)