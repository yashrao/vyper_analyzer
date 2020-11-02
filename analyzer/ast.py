import os
import subprocess
import json
from visualizer import Visualizer

from nodes import ContractNode
from nodes import AssignmentNode
from nodes import AssertNode
from nodes import BinaryOperatorNode
from nodes import FunctionNode
from nodes import AnnAssignmentNode
from nodes import CallNode
from nodes import StatementNode  # Get rid of
from nodes import VariableNode
from nodes import SubscriptNode
from nodes import ConstantNode
from nodes import KeywordNode
from nodes import IfStatementNode
from nodes import ForNode
from nodes import ReturnNode
from nodes import AttributeNode
from nodes import HashMapNode

from nodes import ArrayType
from nodes import PublicType

from pprint import pprint  # DEBUG

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
    'Eq': '==',
    'NotEq': '!=',
}


class AstWalker:
    def __init__(self, filename: str):
        self._contract_name = ''
        self._ast = self.get_ast(filename)
        self._filename = filename

    def walk(self, node, nodes):
        if 'FunctionDef' in node['ast_type']:
            nodes.append(node)
        if "body" in node and node["body"]:
            for child in node["body"]:
                self.walk(child, nodes)

    def get_ast(self, filename: str) -> dict:
        cmd = 'vyper -f ast {}'.format(filename)
        print()
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

    def get_contract_name(self) -> str:
        return self._contract_name

    def get_vyper_src(self, filename: str) -> str:
        with open(filename, 'r') as f:
            return f.read()

    def parse_ast(self, ast:dict) -> list:
        #TODO: Change this to just parse_ast
        body = ast['body']
        statements = [] # Empty list of Strings
        for statement in body:
            statements.append(self.parse_statements(statement))
        #TODO: change 'TODO' string to the actual source code
        vyper_source = self.get_vyper_src(self._filename)
        main = ContractNode(self._contract_name, statements, vyper_source)
        return main

    def parse_statements(self, statement: dict):
        # TODO: handle AnnAssign nodes here
        # TODO: MAKE THIS THE BETTER PARSE_STATMEENTS FUNCTION
        ast_type = self.get_ast_type(statement)
        loc = (statement['col_offset'], statement['end_col_offset'], statement['lineno'])
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
            return FunctionNode(name, body, is_external, decorator_list_res, args, returns, loc)
        elif ast_type == 'AnnAssign':
            #var_type = statement['annotation'] # TODO: turn into a node
            var_type = self.get_right(statement['annotation'], True)
            return AnnAssignmentNode(ast_type, var_type, self.get_left(statement['target']), self.get_right(statement['value']), loc)

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

    def set_state_variable(self, ast_node: dict, node):
        # node is either SuscriptNode or VariableNode
        # ast_node is node from vyper ast dict 
        if 'value' in list(ast_node.keys()):
            if 'id' in list(ast_node['value'].keys()):
                if ast_node['value']['id'] == 'self':
                    # Set as state variable
                    node.set_state_variable(True)

    def parse_body(self, body: list) -> list:
        # TODO: make it prettier (fix the slashes on the end to be on the same column)
        statement_objs = []
        for statement in body:
            ast_type = self.get_ast_type(statement)
            loc = (statement['col_offset'], statement['end_col_offset'], statement['lineno'])
            try:
                if ast_type == 'Assign':
                    left = self.get_left(statement['target'])
                    node = AssignmentNode(ast_type, left, self.get_right(statement['value']), loc)
                    #self.set_state_variable(statement['target'], left)
                    statement_objs.append(node)
                elif ast_type == 'AugAssign':
                    op = self.get_op(statement)
                    left = self.get_left(statement['target'])
                    right = BinaryOperatorNode(ast_type, op, self.get_left(statement['target']), self.get_right(statement['value']), loc)
                    node = AssignmentNode(ast_type, left, right, loc)
                    #self.set_state_variable(statement['target'], left)
                    statement_objs.append(node)
                elif ast_type == 'AnnAssign':
                    if statement['annotation']['ast_type'] != 'Subscript':
                        var_type = statement['annotation']['id']  #TODO: change to a node
                    else:
                        var_type = ArrayType(self.get_left(statement['value']),                        \
                                            statement['annotation']['slice']['value'])
                    left = self.get_left(statement['target'])
                    node = AnnAssignmentNode(ast_type, var_type, left, self.get_right(statement['value']), loc)
                    self.set_state_variable(statement['target'], left)
                    statement_objs.append(node)
                elif ast_type == 'Expr':
                    if 'id' not in list(statement['value']['func'].keys()):
                        if 'keywords' in list(statement['value'].keys()):
                            node = CallNode(statement['value']['func']['value']['id'] + '.' + statement['value']['func']['attr'],                               \
                                self.get_call_args(statement['value']['args'], statement['value']['keywords']), loc)
                        else:
                            node = CallNode(statement['value']['func']['id'], self.get_call_args(statement['value']['args']), loc)
                    else:
                        if 'keywords' in list(statement['value'].keys()):
                            node = CallNode(statement['value']['func']['id'],                               \
                                self.get_call_args(statement['value']['args'], statement['value']['keywords']), loc)
                        else:
                            node = CallNode(statement['value']['func']['id'], self.get_call_args(statement['value']['args']), loc)
                    statement_objs.append(node)
                elif ast_type == 'Assert':
                    if statement['test']['ast_type'] == 'Compare':
                        node = AssertNode(self.get_left(statement['test']['left']),
                            self.get_right(statement['test']['right']),                    \
                            COMPARITORS[statement['test']['op']['ast_type']],              \
                            loc)
                        statement_objs.append(node)
                    elif statement['test']['ast_type'] == 'UnaryOp':
                        #TODO: add the COMPARITOR thing to the assert
                        node = AssertNode(self.get_left(statement['test']['operand']),
                            None,
                            COMPARITORS[statement['test']['op']['ast_type']],
                            loc)
                        statement_objs.append(node)
                elif ast_type == 'If':
                    # TODO: Fix this
                    print('this should be an if statement')
                    test = statement['test']
                    if 'op' not in list(test.keys()):
                        # evals to boolean
                        test_statement = self.get_right(test)
                        body = self.parse_body(statement['body'])
                        orelse = self.parse_body(statement['orelse'])
                        node = IfStatementNode(test_statement, None, test, body, orelse, loc)
                        statement_objs.append(node)
                    elif test['op']['ast_type'] == 'Eq':
                        right = self.get_right(test['right'])
                        left = self.get_right(test['left'])
                        body = self.parse_body(statement['body'])
                        orelse = self.parse_body(statement['orelse'])
                        node = IfStatementNode(left, right, test, body, orelse, loc)
                        statement_objs.append(node)
                elif ast_type == 'For':
                    left = self.get_left(statement['target'])
                    # TODO: check what is considered iterable and apply for all cases
                    iterable = CallNode(statement['iter']['func']['id'],                            \
                            self.get_call_args(statement['iter']['args']),                                \
                                    loc)
                    body = self.parse_body(statement['body'])
                    for_loop = ForNode(left, iterable, body, loc)
                    statement_objs.append(for_loop)
                elif ast_type == 'Return':
                    # TODO: Generalize for all constants not just Int
                    # TODO: change to nodes
                    right = self.get_right(statement['value'])
                    print('')
                    print(statement['value'])
                    print('')
                    #print(right)
                    statement_objs.append(right)
            except KeyError as e:
                pprint(statement)
                raise e
        return statement_objs

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
        return self.get_right(left)
        #ast_type = left['ast_type']
        #loc = (left['col_offset'], left['end_col_offset'], left['lineno'])
        ##if ast_type == 'Subscript':
            #return self.get_left(left['value']) +  \
            #    '[' + self.get_right(left['slice']['value']) + ']
        #    left_var = self.get_left(left['value'])
        #    subscript = self.get_right(left['slice']['value'])
        #    return SubscriptNode(left_var, ast_type, left, subscript, loc)
        #elif ast_type == 'Name':
        #    return VariableNode(left['id'], ast_type, left, loc)
        #elif ast_type == 'Attribute':
        #    return self.get_attr(left)
        #return left['attr']

    def get_attr(self, attr_ast) -> str:
        # Takes in a Vyper Attribute AST node and recursively gets all the attributes
        # value -> value -> value -> ... -> value:id
        # e.g. self.foo.bar == value[value][value][id].value[value][attr].value[attr]
        loc = (attr_ast['col_offset'], attr_ast['end_col_offset'], attr_ast['lineno'])
        ast_type = attr_ast['ast_type']
        #if ast_type == 'Subscript':
        #    attr_ast = attr_ast['value']
        #?if 'value' in list(attr_ast.keys()):
        #    print('LEWL ====')
        #    print(attr_ast)
        #    return self.get_attr(attr_ast['value']) + '.' + attr_ast['attr']
        #else:
        #    return attr_ast['id']
        if ast_type == 'Attribute':
            ret = AttributeNode(self.get_right(attr_ast), self.get_attr(attr_ast['value']), loc)
            print('kelrkerlekrlkerlke')
            print(ret)
            print(attr_ast['attr'])
            #return AttributeNode(self.get_right(attr_ast), self.get_attr(attr_ast['value']), loc)
            return ret
        else:
            return AttributeNode(self.get_right(attr_ast), None, loc)

    ## TODO: Get rid of ast_type if statements
    def get_right(self, right: dict, type=False):
        #TODO: Unary operator needs to be done
        if right == None:
            return None

        ast_type = right['ast_type']
        #print(right)
        loc = (right['col_offset'], right['end_col_offset'], right['lineno'])
        if ast_type == 'Name':
            #(col_offset, end_col_offset, line_no)
            return VariableNode(right['id'], ast_type, right, loc)
        #if ast_type == 'Attribute':
        #    return VariableNode(right['value']['id'] + '.' + right['attr'], ast_type, right, loc)
        if ast_type == 'Int':
            #return VariableNode(right['value'], ast_type, right)
            return ConstantNode(right['value'], loc)
        if ast_type == 'NameConstant':
            #return right['value']
            return ConstantNode(int(right['value']), loc)
        if ast_type == 'BinOp':
            op = self.get_op(right)
            return BinaryOperatorNode(ast_type, op, self.get_right(right['left']), self.get_right(right['right']), loc)
        if ast_type == 'Subscript':
            #TODO: do the case where there is HashMap
            left_var = self.get_left(right['value'])
            print('-==-=-===-=-')
            print(left_var)
            print('-==-=-===-=-')
            #if type(left_var) is VariableNode:
            if isinstance(left_var, VariableNode):
                if left_var.get_identifier() == 'HashMap':
                    # Then this is a hashmap
                    tmp = []
                    for element in right['slice']['elements']:
                        print(element)
                        tmp.append(self.get_right(element))
                    return HashMapNode(tuple(tmp))
            if right['slice']['ast_type'] == 'Name':
                subscript = self.get_right(right['slice'])
            else:
                subscript = self.get_right(right['slice'])
            return SubscriptNode(left_var, ast_type, right, subscript, loc)
        if ast_type == 'Call':
            print('===')
            pprint(right)
            print('===')
            if type:
                return PublicType(self.get_right(right['args'][0]))
            else:
                #TODO: make sure it is able to take into account many attrs
                if 'value' in list(right['func'].keys()):
                    return CallNode(right['func']['attr'],                            \
                            self.get_call_args(right['args']),                                \
                                    loc)
                else:
                    return CallNode(right['func']['id'],                            \
                            self.get_call_args(right['args']),                                \
                                    loc)
            #pprint(right)
        if ast_type == 'Compare':
            op = self.get_op(right)
            return ReturnNode(BinaryOperatorNode(ast_type, op, self.get_right(right['left']), self.get_right(right['right']), loc), loc)
        if ast_type == 'Attribute':
            var = VariableNode(right['attr'], ast_type, right, loc)
            return AttributeNode(var, self.get_attr(right['value']), loc)
        return None

    def get_keyword(self, keyword: dict):
        loc = (keyword['col_offset'], keyword['end_col_offset'], keyword['lineno'])
        return KeywordNode(keyword['arg'], keyword['value']['ast_type'], self.get_right(keyword['value']), loc)

    def get_variable(self, line: dict, body: list):
        pass

    def get_target(self, target: dict) -> str:
        pass

    def get_value(self, value: dict) -> str:
        pass

# TODO: remove
if __name__ == '__main__':
    # ast = AstWalker('example_vyper_contracts/open_auction.vy')
    ast = AstWalker('example_vyper_contracts/vulnerable.vy')
    # ast = AstWalker('example_vyper_contracts/storage.vy')
    nodes = []
    ast.walk(ast._ast, nodes)
    # parsed_ast = visualizer.parse_ast(ast._ast)
    # visualizer.visualize_cfg(parsed_ast)
    parsed_ast = ast.parse_ast(ast._ast)
    visualizer = Visualizer(ast.get_contract_name())
    visualizer.visualize_ast(parsed_ast)
