import os, sys

class frozen(object):
    def app_path():
        if hasattr(sys, 'frozen'):
            return os.path.dirname(sys.executable)
        elif getattr(sys, 'android_app', None):
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                return PythonActivity.mActivity.getFilesDir().getAbsolutePath()
            except Exception:
                return os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.abspath(__file__))

