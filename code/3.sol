// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ComplexChecks {
    uint256 public value;

    // Custom error for revert
    error ValueTooLow(uint256 provided, uint256 required);

    constructor(uint256 _initialValue) {
        value = _initialValue;
    }

    function setValue(uint256 _value) public {
        // Using require to check a condition
        require(_value > 0, "Value must be greater than zero");

        // Using assert to ensure an invariant
        assert(value != _value);

        // Using a function call within require
        require(isEven(_value), "Value must be even");

        // Using revert with a custom error
        if (_value < 10) {
            revert ValueTooLow({provided: _value, required: 10});
        }

        revert();
        revert("This is a revert without a custom error");

        value = _value;
    }

    function isEven(uint256 _value) internal pure returns (bool) {
        return _value % 2 == 0;
    }
}
