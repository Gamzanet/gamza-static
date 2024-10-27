import hashlib
import os.path
from os.path import join

from engine import layer_0
from etherscan.unichain import get_contract_json
from main import project_root
from utils.paths import open_with_mkdir


class Loader:
    def __init__(self, root: str = project_root):
        self._root = root

    @property
    def path_abs_root(self):
        return self._root

    @property
    def path_abs_lib(self):
        return self.as_abs_path("lib")

    @property
    def path_abs_code(self):
        return self.as_abs_path("code")

    @property
    def path_abs_foundry(self):
        return self.as_abs_path("code/unichain")

    @property
    def path_abs_rules(self):
        return self.as_abs_path("rules")

    @property
    def path_abs_output(self) -> str:
        return self.as_abs_path("out")

    def as_abs_path(self, path: str) -> str:
        if self.is_path_rel(path):
            return join(self.path_abs_root, path)
        return path

    @staticmethod
    def is_path_rel(path):
        return (not os.path.exists(path)
                or path.startswith(".")
                or not path.startswith("/"))

    def write_only_if_not_exists(self, path, content):
        if not os.path.exists(self.as_abs_path(path)):
            self.overwrite(path, content)

    def read_rule(self, path):
        with open(join(self.path_abs_rules, path), "r") as file:
            return file.read()

    def read_code(self, path):
        if self.is_path_rel(path) and type(path) is str:
            path = join(self.path_abs_code, path)
        with open(path, "r") as file:
            return file.read()

    @staticmethod
    def inline_code(content):
        # 0. assume code is already formatted
        # 1. remove comments
        import re
        content = re.sub(r"//[\S ]+", "", content)
        # 2. replace empty lines or multiple spaces to single space
        return re.sub(r"\s+", " ", content)


    @staticmethod
    def fetch_code(address, explorer="blockscout"):
        if explorer == "blockscout":
            key = "source_code"
        else:
            raise NotImplementedError(f"Explorer {explorer} not supported")
        return get_contract_json(address)[key]

    @staticmethod
    def overwrite(path, content):
        with(open_with_mkdir(path, "w")) as file:
            file.write(content)

    @staticmethod
    def get_cache_key(content: str) -> str:
        return hashlib.sha3_256(content.encode()).hexdigest()

    def get_cache_path(self, content: str, extension: str) -> str:
        _key = Loader.get_cache_key(content)
        return join(self.path_abs_output, f"{_key}.{extension}")

    def cache_content(self, content: str, extension: str) -> str:
        """
        Cache content and return the path
        :param content: writable content
        :param extension: file extension
        :return: path to cached file
        """
        _path = self.get_cache_path(content, extension)
        Loader.overwrite(_path, content)
        return _path

    @staticmethod
    def format(_path):
        # TODO: check cache in same directory
        layer_0.format_code(_path)
        # TODO: cache formatted code
