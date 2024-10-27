import os
import sys
from os.path import dirname as _dir, join as _join

_project_root = _dir(_dir(__file__))
os.chdir(_project_root)
sys.path.append(_join(_project_root, "lib"))
