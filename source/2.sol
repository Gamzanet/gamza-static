// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ExampleHook is BaseHook, someOtherContract {
    // State variables
    string public name;
    uint256 public value;

    // Constructor
    constructor(string memory _name, uint256 _value) {
        name = _name;
        value = _value;
    }

    function beforeSwap(address, PoolKey calldata, IPoolManager.SwapParams calldata, bytes calldata)
    external
    override
    returns (bytes4, BeforeSwapDelta, uint24)
    {
        return (bytes4(0), BeforeSwapDelta(0, 0), 0);
    }

    function getHookPermissions() public pure override returns (Hooks.Permissions memory){
        return Hooks.Permissions({
            beforeInitialize: true,
            afterInitialize: true,
            beforeSwap: false,
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
