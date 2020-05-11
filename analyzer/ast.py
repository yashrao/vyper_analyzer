import os
import subprocess
import json
from visualizer import Visualizer

class AstWalker:
    def __init__(self, source: str):
        self._ast = self.get_ast(source)

    def walk(self, node, nodes):
        if 'FunctionDef' in node['ast_type']:
            nodes.append(node)
        if "body" in node and node["body"]:
            for child in node["body"]:
                self.walk(child, nodes)

    def get_ast(self, filename: str) -> dict:
        cmd = 'vyper -f ast %s' % filename
        FNULL = open(os.devnull, 'w')
        vyper_c = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=FNULL)
        return json.loads(vyper_c.communicate()[0].decode('utf-8', 'strict'))['ast']
    

#TODO: remove
if __name__ == '__main__':
    ast = AstWalker('example_vyper_contracts/open_auction.vy')
    #ast = AstWalker('example_vyper_contracts/storage.vy')
    nodes = []
    ast.walk(ast._ast, nodes)
    visualizer = Visualizer()
    visualizer.visualize_cfg(nodes)