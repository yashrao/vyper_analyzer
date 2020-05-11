from graphviz import Digraph
from pprint import pprint

AST_TYPES = {
  'Assign': '=',
  'AugAssign': {
    'Add': '+=',
    'Sub': '-='
  },
}

class Visualizer:
    def __init__(self):
        self._graph = Digraph('G', filename='test.png')
        self._graph.attr(overlap='false', 
                name='cfg', 
                label= 'filename.txt', 
                color='black', 
                labelloc='t')
                
    def get_func_label(self, args: list, 
            decorator_list: list, 
            node_name: str) -> str:
        for decorator in decorator_list:
            ret = '@{}\n'.format(decorator['id'])
        ret += node_name + ' ('
        for arg in args:
            if len(args) > 1:
                ret += '{} {}\n'.format(arg['annotation']['id'], arg['arg'])
            else:
                ret += '{} {}'.format(arg['annotation']['id'], arg['arg'])
        ret += ')'
        return ret

    def get_variable(self, line: dict, body: list):
        ast_type = line['ast_type']
        node_struct_str = ''
        if ast_type == 'Assign':
            if line['value']['ast_type'] == 'Name':
                node_struct_str += '{} {} {}'.format(
                    line['target']['attr'], 
                    AST_TYPES[ast_type], 
                    line['value']['id']) 
            elif line['value']['ast_type'] == 'Attribute':
                # TODO: Change this for attributes of attributes
                node_struct_str += '{} {} {}.{}'.format(
                    line['target']['attr'], 
                    AST_TYPES[ast_type], 
                    line['value']['attr'],
                    line['value']['value']['id']) 
            if len(body) > 1:
                node_struct_str += ' |'
        elif ast_type == 'AugAssign':
            op = AST_TYPES['AugAssign'][line['op']['ast_type']]
            node_struct_str += '{} {} {}'.format(
                line['target']['attr'], 
                op, line['value']['value']) 
            if len(body) > 1:
                node_struct_str += ' |'
        return node_struct_str
    ##
    # Pass a list of FunctionDef nodes
    def visualize_cfg(self, nodes: list):
      # Each node 
      for node in nodes:
        with self._graph.subgraph(name='cluster_' + node['name']) as sg:
          node_label = self.get_func_label(node['args']['args'], 
            node['decorator_list'], 
            node['name']) 
        for line in node['body']:
            #TODO: Try/Except for debug/error handling
            try:
                if 'target' in line.keys():
                    sg.attr(label=node_label, 
                        style='dashed', 
                        color='black', 
                        labelloc='t', 
                        rank='same')
                    sg.node(node['name'], 'ENTRY', shape='Mdiamond')
                    node_struct_str = '{ '
                    ast_type = line['ast_type']
                    body = node['body']
                    node_struct_str = self.get_variable(line, body)
                        
                    node_struct_str += '}'
                    sg.node_attr = {'shape': 'record'}
                    #make sure its formatted as a raw string
                    sg.node('struct_' + node['name'], 
                      r'{}'.format(node_struct_str)) 
                   
                    sg.node(node['name'] + '_exit', 'EXIT', shape='Mdiamond')
                    sg.edge(node['name'], 'struct_' + node['name'])
                    sg.edge('struct_' + node['name'], node['name'] + '_exit')
                    sg.edge_attr.update(color='blue', weight='100')
            except KeyError as e:
                pprint(line)
                raise e
              
      self._graph.view() # TODO: Remove

    def save_to_png(self):
        pass