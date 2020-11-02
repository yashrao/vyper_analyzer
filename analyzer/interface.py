import argparse
import os
import json
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

    def get_files(self, path: str, recursive: bool) -> list:
        if os.path.isdir(path):
            if recursive:
                ret = glob(path + '/*.vy', recursive=True)
            else:
                ret = glob(path + '/*.vy', recursive=False)
        else:
            ret = [path]
        return ret

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
        #TODO: Add CLI mode
        parser = argparse.ArgumentParser(description='Vyper Static Analysis Tool')
        parser.add_argument('--format', type=str, nargs='?',
                           help='format options: cfg, ast')
        parser.add_argument('filename', metavar='file-name', type=str, nargs='?',
                           help='Name of the .vy file')
        parser.add_argument('--options', type=str, nargs='+',
                           help='format options: cfg, ast')
        parser.add_argument('--config', type=str, nargs='?',
                           help='--config [specify path to config]')

        args = vars(parser.parse_args())
        print(args)
        files = args['filename']
        visualize = [args['format']]
        config = args['config']
        #TODO: make recursive useful for CLI
        recursive = False
        if not config:
            if files is None and visualize == [None]:
                analyzer_gui = AnalyzerGui()
                analyzer_gui.run()
                user_info = analyzer_gui.get_user_info()
                print(user_info)
                files = user_info['filename']
                visualize = user_info['visualization']
                recursive = user_info['recursive']
                if user_info['filename'] is None:
                    print('Error: Must specify a filename')
                    exit(1)

            if visualize is not None:
                if visualize == [None]:
                    print('Error: Invalid option for format')
                    parser.print_help()
                    exit(1)

                if 'cfg' in visualize:
                    ## Visualize CFG
                    print('Visualize CFG Option enabled')
                if 'ast' in visualize :
                    print('Visualize AST Option enabled')
        else:
            settings = None
            with open(config) as f:
                settings = json.load(f)
            if not settings:
                print('Error: Config file could not be read')
                exit(1)

            files = settings['files'][0]
            visualize = settings['visualization']
            recursive = settings['recursion']
            if 'cfg' in visualize:
                ## Visualize CFG
                print('Visualize CFG Option enabled')
            if 'ast' in visualize :
                print('Visualize AST Option enabled')

        files = self.get_files(files, recursive)
        for file in files:
            # Setup
            ast = AstWalker(file)
            nodes = []
            ast.walk(ast._ast, nodes)
            filename = self.get_filename(file)
            parsed_ast = ast.parse_ast(ast._ast) # process AST

            if visualize:
                visualizer = Visualizer(parsed_ast, ast.get_contract_name())
                if 'cfg' in visualize:
                    print('Visualizing CFG...')
                    visualizer.visualize_cfg()
                    print('Done')
                if 'ast' in visualize:
                    print('Visualizing AST...')
                    visualizer.visualize_ast()
                    print('Done')
            else:
                #print(parsed_ast)
                detector = Detector(parsed_ast)
                detector.public_var_warning()
                #detector.type_check()
                detector.delegate_call_check()
