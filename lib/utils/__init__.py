__all__ = ["unichain", "verify_script", "paths", "project_root_abs", "foundry_dir"]

import os
from os.path import dirname as _dir

from dotenv import load_dotenv

load_dotenv()

_network = "unichain"
_cache_base = os.path.join("code", _network)
foundry_dir: str = os.path.join("code", "unichain")
project_root_abs = os.path.abspath(_dir(_dir(_dir(__file__))))
