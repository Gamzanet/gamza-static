__all__ = ["unichain", "verify_script"]

import os

from dotenv import load_dotenv

load_dotenv()
_network = "unichain"
_cache_base = os.path.join("code", _network)
foundry_dir: str = os.path.join("code", "unichain")
