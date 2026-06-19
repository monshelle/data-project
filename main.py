import sys
import os
import importlib.util

if __name__ == '__main__':
    _root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(_root, 'src'))

    _spec = importlib.util.spec_from_file_location(
        'src_main', os.path.join(_root, 'src', 'main.py')
    )
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    _mod.main()
