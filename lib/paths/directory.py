import os
from typing import TextIO


def open_with_mkdir(file_path: str, mode: str) -> TextIO:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    return open(file_path, mode)
