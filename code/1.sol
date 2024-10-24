// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ExampleHook is BaseHook {
    // State variables
    string public name;
    uint256 public value;

    // Constructor
    constructor(string memory _name, uint256 _value) {
        name = _name;
        value = _value;
    }

    function iterativeIfElse(uint256 x) public pure returns (uint256) {
        if (x == 0) {
            return 0;
        } else if (x == 1) {
            return 1;
        } else if (x >= 2) {
            if (x == 3) {
                return 3;
            } else if (x == 4) {
                return 4;
            } else {
                return 2;
            }
        } else {
            return 5;
        }
    }
}
