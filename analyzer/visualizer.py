from graphviz import Digraph
from pprint import pprint

from nodes import *
import os

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
    def __init__(self, parsed_ast: ContractNode, filename):
        self._graph = Digraph('G', filename='filename.txt') # TODO: change the filename
        self._graph.attr(overlap='false', 
                name='cfg', 
                label= filename, 
                color='black', 
                labelloc='t')
        self._filename = filename
        self._parsed_ast = parsed_ast
                
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

    def build_right(self, node_label, sg, right, prev, count):
        # If prev = None then it is the start of the tree
        if type(right) is BinaryOperatorNode:
            node_label_statement = node_label + '_' + OPERATORS[right.get_op()] + str(count) 
            sg.node(node_label_statement, label=OPERATORS[right.get_op()])
            count += 1
            sg.edge(prev, node_label_statement)
            self.build_right(node_label, sg, right.get_left(), node_label_statement, count)
            self.build_right(node_label, sg, right.get_right(), node_label_statement, count)
        elif type(right) is ConstantNode:
            ## just return the string
            node_label_statement = node_label + '_' + str(right.get_value()) + str(count) 
            sg.node(node_label_statement, label=str(right.get_value()))
            sg.edge(prev, node_label_statement)
            count += 1
        elif type(right) is VariableNode:
            node_label_statement = node_label + '_' + right.get_identifier() + str(count) 
            sg.node(node_label_statement, label=right.get_identifier())
            sg.edge(prev, node_label_statement)
            count += 1
        

    def visualize_ast(self):
        """ Used to visualize the AST into graphviz format
        nodes: list of FunctionNode objects containing a list of StatementNode objects
        """
        output_folder = self.create_output_folder_ast()
        nodes = self._parsed_ast.get_body()
        for node in nodes:
            if node is None or type(node) is not FunctionNode:
                continue
            with self._graph.subgraph(name='cluster_' + node.get_name()) as sg:
                node_label = self.get_func_label(node.get_name(), 
                    node.get_decorator_list(), 
                    node.get_arg_list())
                #node_label = ''.join(''.join(self.get_func_label(node.get_name(), 
                #    node.get_decorator_list(), 
                #    node.get_arg_list()).split(' ')).split('\n'))
                sg.attr(label=node_label)
                sg.attr(style='filled', color ='lightgrey')
                #sg.node(node_label, 'Function: ' + node_label, shape='Mdiamond', fillcolor='white')

                body = node.get_body()
                count = 0
                #sg.node(node_label + '_start', label='START')
                for statement in body:
                    #this part needs to call some kind of recursive function 
                    print(statement)
                    print(node_label)
                    if type(statement) is AssignmentNode:
                        left = statement.get_left()
                        if type(left) is SubscriptNode:
                            print('lol' + str(left.get_subscript()))
                        elif type(left) is VariableNode:
                            sg.node(node_label +'=' + '_' + str(count), label='=')
                            tmp = node_label + '=' + '_' + str(count)
                            count += 1
                            identifier = left.get_identifier()
                            node_label_statement = node_label + '_' + identifier + str(count) # lvalue
                            print('lol' + node_label_statement)
                            sg.node(node_label_statement, label=identifier) # lvalue must be variablenode
                            count += 1
                            sg.edge(tmp, node_label_statement)
                            self.build_right(node_label, sg, statement.get_right(), tmp, count)
                    #node_label_statement = node_label + '_' + str(count)
                    #value = str(statement.get_value())
                    #target = str(statement.get_target())
                    #identifier = str(statement.get_identifier())
                    #sg.node(node_label_statement + '_identifier', label=identifier)
                    #sg.node(node_label_statement + '_target', label=target)
                    #sg.node(node_label_statement + '_value', label=value)
                    #sg.edge(node_label + '_identifier', node_label_statement + '_target')
                    #sg.edge(node_label + '_identifier', node_label_statement + '_value')
                    #if count == 0:
                    #    sg.edge(node_label + '_start', node_label_statement)
                    #count += 1
                
        self._graph.render(output_folder + '/' + self._filename)

    def visualize_cfg_new(self, parsed_ast: ContractNode):
        pass
        
    def create_output_folder_ast(self) -> str:
        OUTPUT_DIR = 'output'
        AST_DIR = 'ast'
        if not os.path.isdir(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        if not os.path.isdir(OUTPUT_DIR + '/' + AST_DIR):
            os.makedirs(OUTPUT_DIR + '/' + AST_DIR)
        return OUTPUT_DIR + '/' + AST_DIR

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