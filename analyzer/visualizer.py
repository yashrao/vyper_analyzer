"""
Used for accessing files
"""
import os

from graphviz import Digraph
#from pprint import pprint

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

"""
TODO:
"""
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
            # checking if unit is array type or not
            if 'slice' in arg['annotation'].keys():
                slice_val = arg['annotation']['slice']['value']['value'] #TODO: generalize into a function
                arg_id = '{}[{}] {}'.format(arg['annotation']['value']['id'], slice_val, arg['arg'])
            else:
                arg_id = '{} {}'.format(arg['annotation']['id'], arg['arg'])
            if len(args) > 1:
                ret += '{}\n'.format(arg_id)
            else:
                ret += '{}'.format(arg_id)
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
        
    def build_subscript_str(self, node) -> str:
        # Possible Nodes: Variable, Constant, Subscript, BinOp
        subscript_str = '['
        node_type = type(node)
        if node_type is VariableNode:
            subscript_str += node.get_identifier()
        #TODO: the below needs to be tested
        elif node_type is ConstantNode:
            subscript_str += str(node.get_value())
        elif node_type is SubscriptNode:
            subscript_str += node.get_left() + self.build_subscript_str(node.get_subscript())
        elif node_type is BinaryOperatorNode:
            subscript_str += self.build_subscript_str(node.get_left()) +   \
                OPERATORS[node.get_op()] +                  \
                self.build_subscript_str(node.get_right())
        
        return subscript_str + ']'

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
                sg.attr(label=node_label)
                sg.attr(style='filled', color ='lightgrey')

                body = node.get_body()
                count = 0
                for statement in body:
                    #this part needs to call some kind of recursive function 
                    print(statement)
                    print(node_label)
                    if type(statement) is AssignmentNode:
                        left = statement.get_left()
                        if type(left) is SubscriptNode:
                            sg.node(node_label +'=' + '_' + str(count), label='=')
                            tmp = node_label + '=' + '_' + str(count)
                            count += 1
                            identifier = left.get_left().get_identifier() +                \
                                self.build_subscript_str(left.get_subscript()) 
                            node_label_statement = node_label + '_' + identifier + str(count) # lvalue
                            sg.node(node_label_statement, label=identifier) # lvalue must be variablenode
                            count += 1
                            sg.edge(tmp, node_label_statement)
                            self.build_right(node_label, sg, statement.get_right(), tmp, count)
                        elif type(left) is VariableNode:
                            sg.node(node_label +'=' + '_' + str(count), label='=')
                            tmp = node_label + '=' + '_' + str(count)
                            count += 1
                            identifier = left.get_identifier()
                            node_label_statement = node_label + '_' + identifier + str(count) # lvalue
                            sg.node(node_label_statement, label=identifier) # lvalue must be variablenode
                            count += 1
                            sg.edge(tmp, node_label_statement)
                            self.build_right(node_label, sg, statement.get_right(), tmp, count)
                    elif type(statement) is CallNode:
                        identifier = statement.get_call()
                        call_node_label = node_label + '_' + identifier + str(count) # lvalue
                        sg.node(call_node_label, label='FunctionCall(' + identifier + ')')
                        count += 1
                        param_list = statement.get_param_list()
                        for param in param_list:
                            self.build_right(node_label, sg, param, call_node_label, count)
                
        self._graph.render(output_folder + '/' + self._filename)

    def build_right_statement_cfg(self, right) -> str:
        if type(right) is BinaryOperatorNode:
            print(right)
            op = OPERATORS[right.get_op()]
            lval = right.get_left()
            if type(lval) is VariableNode:
                return lval.get_identifier() + op + self.build_right_statement_cfg(right.get_right())
            elif type(lval) is SubscriptNode:
                return lval.get_left().get_identifier() +                \
                    self.build_subscript_str(lval.get_subscript()) 
        #TODO: if right is a subscript 
        if type(right) is ConstantNode:
            return str(right.get_value())
        return right.get_identifier()

    
    def visualize_cfg_new(self):
        output_folder = self.create_output_folder_cfg()
        nodes = self._parsed_ast.get_body()
        for node in nodes:
            if node is None or type(node) is not FunctionNode:
                continue
            with self._graph.subgraph(name='cluster_' + node.get_name()) as sg:
                node_label = self.get_func_label(node.get_name(), 
                    node.get_decorator_list(), 
                    node.get_arg_list()) 
                sg.attr(label=node_label)
                sg.node(node_label, 'ENTRY', shape='Mdiamond', fillcolor='white')
                body = node.get_body()

                node_struct_str = '{'
                
                for i in range(len(body)):
                    statement = body[i]
                    node_struct_str += '{'
                    if type(statement) is AssignmentNode:
                        left = statement.get_left()
                        if type(left) is SubscriptNode:
                            identifier = left.get_left().get_identifier() +                \
                                self.build_subscript_str(left.get_subscript()) 
                            right = self.build_right_statement_cfg(statement.get_right())
                            node_struct_str += identifier + ' = ' + right
                        elif type(left) is VariableNode:
                            right = self.build_right_statement_cfg(statement.get_right())
                            node_struct_str += left.get_identifier() + ' = ' + right
                    elif type(statement) is CallNode:
                        identifier = statement.get_call()
                        print(identifier)
                        param_list = statement.get_param_list()
                        param_list_str = '('
                        for i in range(len(param_list)):
                            param = param_list[i]
                            if len(param_list) == 1:
                                param_list_str += self.build_right_statement_cfg
                            else:
                                if i == len(param_list) - 1:
                                    param_list_str += self.build_right_statement_cfg(param)
                                else:
                                    param_list_str += self.build_right_statement_cfg(param) + ', '
                        param_list_str += ')'
                        node_struct_str += identifier + param_list_str
                    elif type(statement) is AssertNode:
                        print('lkek')
                        if statement.get_right() is not None:
                            node_struct_str += 'assert ' + self.build_right_statement_cfg(statement.get_left()) \
                                    + ' ' + statement.get_comparitor() + ' '                                    \
                                    + self.build_right_statement_cfg(statement.get_right())
                        else:
                            node_struct_str += 'assert '                                                        \
                                    + ' ' + statement.get_comparitor() + ' '                                    \
                                    + self.build_right_statement_cfg(statement.get_left())
                        
                    #node_struct_str += body[i]
                    if i != len(body) - 1:
                        node_struct_str += '}|'
                    else:
                        node_struct_str += '}'
                sg.edge(node_label, 'struct_' + node.get_name())

                node_struct_str += '}'

                sg.node_attr = {
                    'shape': 'record', 
                    'style':'filled',
                    'fillcolor':'lightgrey'
                }
                sg.node('struct_' + node.get_name(), 
                  r'{}'.format(node_struct_str)) 

                print(node_struct_str)
                
        self._graph.render(output_folder + '/' + self._filename)
        
    def create_output_folder_ast(self) -> str:
        OUTPUT_DIR = 'output'
        AST_DIR = 'ast'
        if not os.path.isdir(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        if not os.path.isdir(OUTPUT_DIR + '/' + AST_DIR):
            os.makedirs(OUTPUT_DIR + '/' + AST_DIR)
        return OUTPUT_DIR + '/' + AST_DIR
        
    def create_output_folder_cfg(self) -> str:
        OUTPUT_DIR = 'output'
        CFG_DIR = 'cfg'
        if not os.path.isdir(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        if not os.path.isdir(OUTPUT_DIR + '/' + CFG_DIR):
            os.makedirs(OUTPUT_DIR + '/' + CFG_DIR)
        return OUTPUT_DIR + '/' + CFG_DIR

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
