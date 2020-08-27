import argparse
import os
from ast import AstWalker 
from visualizer import Visualizer
from detector import Detector

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
                           help='format options: cfg, ast')
        parser.add_argument('filename', metavar='file-name', type=str, nargs='+',
                           help='Name of the .vy file')

        args = vars(parser.parse_args())
        print(args)
        files = args['filename']
        visualize = args['format']
        if visualize is not None:
            if 'cfg' == visualize:
                ## Visualize CFG
                print('Visualize CFG Option enabled')
            elif 'ast' == visualize :
                print('Visualize AST Option enabled')
            else: 
                print('ERROR: Invalid option for format')
                parser.print_help()
                exit(1)

        for file in files:
            # Setup
            ast = AstWalker(file)
            nodes = []
            ast.walk(ast._ast, nodes)
            filename = self.get_filename(file)
            parsed_ast = ast.parse_ast(ast._ast) # process AST
            
            if visualize:
                visualizer = Visualizer(parsed_ast, ast.get_contract_name())
                if visualize == 'cfg':
                    visualizer.visualize_cfg_new()
                elif visualize == 'ast':
                    visualizer.visualize_ast()
            else:
                #print(parsed_ast)
                detector = Detector(parsed_ast)
                #detector.public_var_warning()
                #detector.type_check()
                #detector.delegate_call_check()
                #print(filename)
                #visualizer.visualize_ast(parsed_ast, filename)


