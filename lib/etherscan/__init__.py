__all__ = ["ether_api_call", "verify_script", "get_sources_by_pool_key"]

import os

from dotenv import load_dotenv

load_dotenv()
os.chdir(os.path.dirname(__file__))
