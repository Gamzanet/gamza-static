// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./BaseHook.sol";

contract ExampleHook is BaseHook {
    // State variables
    string public name;
    uint256 public value;

    // Constructor
    constructor(string memory _name, uint256 _value) {
        name = _name;
        value = _value;
    }

    function getHookPermissions() public pure override returns (Hooks.Permissions memory){
        return Hooks.Permissions({
            beforeInitialize: true,
            afterInitialize: true,
            beforeSwap: true,
            afterSwap: true,
            beforeAddLiquidity: true,
            afterAddLiquidity: true,
            beforeRemoveLiquidity: true,
            afterRemoveLiquidity: true,
            beforeDonate: true,
            afterDonate: true
        });
    }
}
