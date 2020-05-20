from graphviz import Digraph
from pprint import pprint

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

class Visualizer:
    def __init__(self, filename):
        self._graph = Digraph('G', filename='filename.txt') # TODO: change the filename
        self._graph.attr(overlap='false', 
                name='cfg', 
                label= filename, 
                color='black', 
                labelloc='t')
                
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

    def parse_statements(self, statement: dict):
        # TODO: handle AnnAssign nodes here
        ast_type = self.get_ast_type(statement)
        if ast_type == 'FunctionDef':
            body = self.parse_body(statement['body']) # Returns a list of statements 
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

    def parse_body(self, body: list) -> list:
        statements = []
        for statement in body:
            ast_type = self.get_ast_type(statement)
            print(ast_type) 
            try:
                if ast_type == 'Assign':
                    statements.append('{} {} {}'.format(
                            self.get_left(statement['target'], statement['target']['ast_type']), 
                            AST_TYPES['Assign'],
                            self.get_right(statement['value'], statement['value']['ast_type'])))
                elif ast_type == 'AugAssign':
                    op = self.get_op(statement) 
                    statements.append('{} {} {}'.format(
                            self.get_left(statement['target'], statement['target']['ast_type']), 
                            AST_TYPES['AugAssign'][op],
                            self.get_right(statement['value'], statement['value']['ast_type'])))
                elif ast_type == 'Return':
                    statements.append('return {}'.format(statement['value']['attr']))
            except KeyError as e:
                pprint(statement)
                raise e
        print(statements)
        return statements

    def get_ast_type(self, statement: dict):
        return statement['ast_type']

    def get_op(self, statement: dict):
        return statement['op']['ast_type']

    def get_aug_operator(self, ast_type: str) -> str:
        return AST_TYPES['AugAssign'][ast_type] 

    # Get left hand side of a assignment
    def get_left(self, left: dict, ast_type: str) -> str:
        ## TODO: make get_left take statement['target]
        if ast_type == 'Subscript':
            return left['value']['attr'] + '[' + left['slice']['value']['attr'] + ']'
        return left['attr']

    # Get right hand side of an assignment
    ## TODO: Get rid of ast_type if statements
    def get_right(self, right: dict, ast_type: str) -> str:
        if ast_type == 'Name':
            return right['id']
        elif ast_type == 'Attribute':
            return right['attr'] 
        elif ast_type == 'Int':
            return right['value']
        ## TODO: change this entirely

    def get_variable(self, line: dict, body: list):
        pass

    def get_target(self, target: dict) -> str:
        pass

    def get_value(self, value: dict) -> str:
        pass
    
    # List of statement nodes and function nodes
    def visualize_cfg(self, nodes: list):
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
        self._graph.render('test')

    ##
    def save_to_png(self):
        pass