from helpers import *
import importlib
__builtins__['reload'] = importlib.reload
__builtins__['ue'] = ue
__builtins__['log'] = log

class Runner():
    @property
    def r(self):
        filename = r'c:\temp\p.py'
        print('== loading ' + filename + ' ==')
        ue.exec(os.path.expanduser(filename))

__builtins__['r'] = Runner()

