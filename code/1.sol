// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Test {
    function a() public {
        if (x > 0) {
            if (y > 0) {
                // do nothing
                a;
            }
        }

        if (x > 0) {
            revert(); // ✅ #1 revert:(x > 0)
            for (int i = 0; i < 10; i++) {
                if (i == 0) {
                    revert(); // ✅ #2 revert:(#1 and (i == 0))
                } else if (i == 1) {
                    assert(y > 0); // ✅ #3 assert:((#1 and ((i == 1) and not(#2) and (y > 0))) and y > 0)
                }
            }
            x > 0;
            if (y > 0) {
                revert(); // ✅ #4 revert:(y > 0)
            } else if (z > 0) {
                assert(k > 0); // ✅ #5 assert:((z > 0) and not(#4)) and k > 0)
            } else {
                require(y > 0 || z > 0); // ✅ #6 require:(not(((z > 0) and not((y > 0)))) and y > 0 or z > 0)
            }
        }
    }
}
