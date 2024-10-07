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

    function getHookPermissions() public pure override returns (Hooks.Permissions memory){
        return Hooks.Permissions({
            beforeInitialize: false,
            afterInitialize: false,
            beforeSwap: true,
            afterSwap: false,
            beforeAddLiquidity: false,
            afterAddLiquidity: false,
            beforeRemoveLiquidity: false,
            afterRemoveLiquidity: false,
            beforeDonate: false,
            afterDonate: false
        });
    }
}
