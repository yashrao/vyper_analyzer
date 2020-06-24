from graphviz import Digraph
from pprint import pprint

from nodes import *

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

class Visualizer:
    def __init__(self, filename):
        self._graph = Digraph('G', filename='filename.txt') # TODO: change the filename
        self._graph.attr(overlap='false', 
                name='cfg', 
                label= filename, 
                color='black', 
                labelloc='t')
        self._filename = filename
                
    def get_func_label(self, node_name: str, 
            decorator_list: list, 
            args: list) -> str:
        for decorator in decorator_list:
            ret = '@{}\n'.format(decorator)
        ret += node_name + ' ('
        for arg in args:
            if len(args) > 1:
                ret += '{} {}\n'.format(arg['annotation']['id'], arg['arg'])
            else:
                ret += '{} {}'.format(arg['annotation']['id'], arg['arg'])
        ret += ')'
        return ret

    def parse_ast(self, ast: dict) -> list:
        body = ast['body']
        statements = [] # Empty list of Strings
        for statement in body:
            statements.append(self.parse_statements(statement))
        print(statements)
        return statements

    def parse_ast_alt(self, ast:dict) -> list:
        body = ast['body']
        statements = [] # Empty list of Strings
        for statement in body:
            statements.append(self.__parse_statements(statement))
        print(statements)
        return statements

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
        

    def __parse_body(self, body: list) -> list:
        # TODO: make it prettier (fix the slashes on the end to be on the same column)
        statement_objs = []
        for statement in body:
            ast_type = self.get_ast_type(statement)
            print(ast_type) 
            try:
                if ast_type == 'Assign':
                    statement_objs.append(StatementNode(ast_type, AST_TYPES['Assign'],                      \
                            self.get_left(statement['target']),                                             \
                            self.get_right(statement['value'])))
                    print('THIS IS A TEST <><><><> {}'.format(self.__get_right(statement['value'])))
                elif ast_type == 'AugAssign':
                    op = self.get_op(statement) 
                    statement_objs.append(StatementNode(ast_type, AST_TYPES['AugAssign'][op],               \
                            self.get_left(statement['target']),                                             \
                            self.get_right(statement['value'])))
                elif ast_type == 'AnnAssign':
                    statement_objs.append(StatementNode(ast_type, statement['annotation']['id'],            \
                            self.get_left(statement['target']),                                             \
                            self.get_right(statement['value'])))
                elif ast_type == 'Expr':
                    statement_objs.append(StatementNode(ast_type, 'Call', 
                            statement['value']['func']['id'],                                               \
                            self.get_func_args(statement['value']['args'])))
                elif ast_type == 'Assert':
                    if statement['test']['ast_type'] == 'Compare':
                        statement_objs.append(StatementNode(ast_type, self.get_left(statement['test']['left']), \
                            COMPARITORS[statement['test']['op']['ast_type']],                                  \
                            self.get_right(statement['test']['right'])))
                    elif statement['test']['ast_type'] == 'UnaryOp':
                        statement_objs.append(StatementNode(ast_type, None,                                     \
                            COMPARITORS[statement['test']['op']['ast_type']],                                  \
                            self.get_right(statement['test']['operand'])))
                elif ast_type == 'Return':
                    # TODO: Generalize for all constants not just Int
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
        ast_type = left['ast_type']
        if ast_type == 'Subscript':
            return self.get_left(left['value']) +  \
                '[' + self.get_right(left['slice']['value']) + ']'
        elif ast_type == 'Attribute':
            return left['value']['id'] + '.' + left['attr']
        elif ast_type == 'Name':
            return left['id']
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
        ast_type = right['ast_type']
        if ast_type == 'Name':
            return VariableNode(right['id'], ast_type, right)
        elif ast_type == 'Attribute':
            return VariableNode(right['value']['id'] + '.' + right['attr'], ast_type, right)
        elif ast_type == 'Int':
            return VariableNode(right['value']['id'] + '.' + right['attr'], ast_type, right)
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
    
    def visualize_ast(self, nodes: list):
        """ Used to visualize the AST into graphviz format
        nodes: list of FunctionNode objects containing a list of StatementNode objects
        """
        for node in nodes:
            if node is None:
                continue
            with self._graph.subgraph(name='cluster_' + node.get_name()) as sg:
                node_label = self.get_func_label(node.get_name(), 
                    node.get_decorator_list(), 
                    node.get_arg_list()) 
                sg.attr(label=node_label)
                sg.attr(style='filled', color ='lightgrey')
                #sg.node(node_label, 'Function: ' + node_label, shape='Mdiamond', fillcolor='white')

                body = node.get_body()
                count = 0
                sg.node(node_label + '_start', label='START')
                for statement in body:
                    print(statement)
                    node_label_statement = node_label + '_' + str(count)
                    value = str(statement.get_value())
                    target = str(statement.get_target())
                    identifier = str(statement.get_identifier())
                    sg.node(node_label_statement + '_identifier', label=identifier)
                    sg.node(node_label_statement + '_target', label=target)
                    sg.node(node_label_statement + '_value', label=value)
                    sg.edge(node_label + '_identifier', node_label_statement + '_target')
                    sg.edge(node_label + '_identifier', node_label_statement + '_value')
                    if count == 0:
                        sg.edge(node_label + '_start', node_label_statement)
                    count += 1
                
        self._graph.render('test_alt')

    # List of statement nodes and function nodes
    def visualize_cfg(self, nodes: list):
        #TODO: change this so that it uses the new StatementNode instead
        for node in nodes:
            if node is None: # TODO: REMOVE THIS
                continue
            with self._graph.subgraph(name='cluster_' + node.get_name()) as sg:
                node_label = self.get_func_label(node.get_name(), 
                    node.get_decorator_list(), 
                    node.get_arg_list()) 
                sg.attr(label=node_label)
                sg.node(node_label, 'ENTRY', shape='Mdiamond', fillcolor='white')

                node_struct_str = '{'
                print(node.get_body())
                body = node.get_body()
                for i in range(len(body)):
                    node_struct_str += '{'
                    node_struct_str += body[i]
                    if i != len(body) - 1:
                        node_struct_str += '}|'
                    else:
                        node_struct_str += '}'

                node_struct_str += '}'
                print(node_struct_str)

                sg.node_attr = {
                    'shape': 'record', 
                    'style':'filled',
                    'fillcolor':'lightgrey'
                }
                sg.node('struct_' + node.get_name(), 
                  r'{}'.format(node_struct_str)) 
                
                returns = 'None'
                if node.get_returns() != '':
                    returns = node.get_returns()
                sg.node(node.get_name() + '_exit', 
                    'RETURN: ' + returns, 
                    shape='Mdiamond', 
                    fillcolor='white')
                sg.edge(node_label, 'struct_' + node.get_name())
                sg.edge('struct_' + node.get_name(), 
                    node.get_name() + '_exit')
                sg.edge_attr.update(color='blue', weight='100')
        #self._graph.render(self._filename)
        self._graph.render('test')

    ##
    def save_to_png(self):
        pass