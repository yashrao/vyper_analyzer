import argparse
import os
from ast import AstWalker 
from visualizer import Visualizer
from detector import Detector
from gui import AnalyzerGui
from glob import glob

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

    def get_files(self, path) -> list:
        if os.path.isdir(path):
            files = os.listdir(path)
            ret = []
            for file_ in files:
                ret.append(path + '/' + file_)
            return ret 
        return [path]

    def get_files_recursive(self, path) -> list:
        #TODO: this doesn't work at the moment, but make it recursive so it gets all the folders
        if os.path.isdir(path):
            files = os.listdir(path)
            ret = []
            for file in files:
                if os.path.isdir(path):
                    #get list of files in the folder
                    tmp += os.listdir(path)
                else:
                    ret.append(path)
            return ret 
        return path


    def cli(self):
        parser = argparse.ArgumentParser(description='Vyper Static Analysis Tool')
        parser.add_argument('--format', type=str, nargs='?',
                           help='format options: cfg, ast')
        parser.add_argument('filename', metavar='file-name', type=str, nargs='?',
                           help='Name of the .vy file')
        parser.add_argument('--options', type=str, nargs='+',
                           help='format options: cfg, ast')

        args = vars(parser.parse_args())
        print(args)
        files = args['filename']
        visualize = args['format']
        analyzer_gui = None
        if files is None and visualize is None:
            analyzer_gui = AnalyzerGui()
            analyzer_gui.run()
            user_info = analyzer_gui.get_user_info()
            files = user_info['filename']
            if user_info['filename'] is None:
                print('Error: Must specify a filename')
                exit(1)

        if visualize is not None:
            if 'cfg' == visualize:
                ## Visualize CFG
                print('Visualize CFG Option enabled')
            if 'ast' == visualize :
                print('Visualize AST Option enabled')
            if visualize != 'cfg' and visualize != 'ast':
                print('Error: Invalid option for format')
                parser.print_help()
                exit(1)

        files = self.get_files(files)
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
                    visualizer.visualize_cfg()
                elif visualize == 'ast':
                    visualizer.visualize_ast()
            else:
                #print(parsed_ast)
                detector = Detector(parsed_ast)
                detector.public_var_warning()
                #detector.type_check()
                detector.delegate_call_check()
