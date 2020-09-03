import npyscreen

OPTIONS = ['Type Check', 'DelegateCall Injection Check']
FORMAT_OPTIONS_DISPLAY = ['AST Generation', 'CFG Generation']
FORMAT_OPTIONS = ['ast', 'cfg']

class AnalyzerGui(npyscreen.NPSApp):
    def __init__(self):
#        self._text = """
#        __   ___   _ _ __   ___ _ __    __ _ _ __   __ _| |_   _ _______ _ __\n
#\ \ / | | | | '_ \ / _ | '__   / _` | '_ \ / _` | | | | |_  / _ | '__|\n
# \ V /| |_| | |_) |  __| |    | (_| | | | | (_| | | |_| |/ |  __| |\n
#  \_/  \__, | .__/ \___|_|     \__,_|_| |_|\__,_|_|\__, /___\___|_|\n
#       |___/|_|                                  |___/\n"""
        self._options = {'filename': None, 'options': [], 'visualization': []}

    def get_user_info(self) -> dict:
        return self._options

    def main(self):
        # These lines create the form and populate it with widgets.
        # A fairly complex screen in only 8 or so lines of code - a line for each control.
        F  = npyscreen.Form(name = "Welcome to the Vyper Analyzer",)
        F.add(npyscreen.FixedText, value="Welcome to the Vyper Analyzer")
        fn = F.add(npyscreen.TitleFilenameCombo, name="Location of Vyper file:")
        ms= F.add(npyscreen.TitleMultiSelect, max_height =4, value = [1,], name="Select what to apply",
                values = OPTIONS, scroll_exit=True)
        ms1= F.add(npyscreen.TitleMultiSelect, max_height =4, value = [1,], name="Select visualization",
                values = FORMAT_OPTIONS, scroll_exit=True)

        F.edit()

        self._options['filename'] = fn.value

        for option in ms.value:
            self._options['options'].append(OPTIONS[option])

        for format_option in ms1.value:
            self._options['visualization'].append(FORMAT_OPTIONS[format_option])
