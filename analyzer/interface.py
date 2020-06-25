import argparse
import os
from ast import AstWalker 
from visualizer import Visualizer

class Interface:
    def __init__(self):
        """
        The CLI interface for the application  
        """
        self.cli()

    def get_filename(self, filename: str) -> str:
        # TODO: make this better maybe
        ret = filename.split('/')[-1]
        if '.' in ret:
            ret = ret.split('.')[0]
        return ret

    def get_files(self, files: list) -> str:
        #TODO: this doesn't work at the moment, but make it recursive so it gets all the folders
        ret = []
        for file in files:
            if os.path.isdir(file):
                #get list of files in the folder
                tmp += os.listdir(file)
            else:
                ret.append(file)
        return ret 


    def cli(self):
        parser = argparse.ArgumentParser(description='Vyper Static Analysis Tool')
        parser.add_argument('--format', type=str, nargs='?',
                           help='format options: visualize-cfg, visualize-ast')
        parser.add_argument('filename', metavar='file-name', type=str, nargs='+',
                           help='Name of the .vy file')

        args = vars(parser.parse_args())
        print(args)
        files = args['filename']

        for file in files:
            ast = AstWalker(file)
            nodes = []
            ast.walk(ast._ast, nodes)
            filename = self.get_filename(file)
            visualizer = Visualizer(ast.get_contract_name())
            #parsed_ast = visualizer.parse_ast(ast._ast)
            #visualizer.visualize_cfg(parsed_ast)
            parsed_ast = visualizer.parse_ast_alt(ast._ast)
            print(filename)
            visualizer.visualize_ast(parsed_ast, filename)


