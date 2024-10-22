import os
import sys

os.chdir(os.path.dirname(os.path.dirname(__file__)))
# to run `python main.py` in root dir, add path of library to sys.path
_path_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib"))
sys.path.append(_path_lib)
