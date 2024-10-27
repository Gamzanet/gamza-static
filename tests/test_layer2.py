from jmespath import search

from engine.run_semgrep import get_semgrep_output
from utils.paths import open_with_mkdir


def test_get_inheritance():
    _path = "out/get_inheritance.sol"
    with open_with_mkdir(_path, "w") as f:
        f.write("""// SPDX-License-Identifier: MIT
            pragma solidity ^0.8.0; contract ComplexChecks is A, B, c { } """)
    info_inheritance: list[dict] = get_semgrep_output("info-inheritance", _path)
    assert search("[*].data.INHERIT", info_inheritance) == ["A", "B", "c"]


def test_get_library():
    _path = "out/get_library.sol"
    with open_with_mkdir(_path, "w") as f:
        f.write("""// SPDX-License-Identifier: MIT
            pragma solidity ^0.8.0; contract ComplexChecks  { using A for address; using B for *; } """)
    info_library: list[dict] = get_semgrep_output("info-library", _path)
    assert search("[*].data.LIBRARY", info_library) == ["A", "B"]
