import os
import subprocess
import json
from visualizer import Visualizer

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
    

#TODO: remove
if __name__ == '__main__':
    #ast = AstWalker('example_vyper_contracts/open_auction.vy')
    ast = AstWalker('example_vyper_contracts/vulnerable.vy')
    #ast = AstWalker('example_vyper_contracts/storage.vy')
    nodes = []
    ast.walk(ast._ast, nodes)
    visualizer = Visualizer(ast.get_contract_name())
    #parsed_ast = visualizer.parse_ast(ast._ast)
    #visualizer.visualize_cfg(parsed_ast)
    parsed_ast = visualizer.parse_ast_alt(ast._ast)
    visualizer.visualize_ast(parsed_ast)