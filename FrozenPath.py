import os, sys

class frozen(object):
    def app_path():
        if hasattr(sys, 'frozen'):
            return os.path.dirname(sys.executable)
        return os.path.dirname(__file__)

