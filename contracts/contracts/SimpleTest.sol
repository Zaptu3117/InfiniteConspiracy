// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title SimpleTest
 * @notice Minimal contract to test Paseo testnet functionality
 */
contract SimpleTest {
    uint256 public counter;
    address public owner;
    
    event CounterIncremented(uint256 newValue);
    event ValueReceived(address from, uint256 amount);
    
    constructor() {
        owner = msg.sender;
        counter = 0;
    }
    
    // Simple non-payable function
    function increment() external {
        counter++;
        emit CounterIncremented(counter);
    }
    
    // Simple payable function
    function receiveValue() external payable {
        emit ValueReceived(msg.sender, msg.value);
    }
    
    // Function with access control
    function ownerIncrement() external {
        require(msg.sender == owner, "Not owner");
        counter += 10;
        emit CounterIncremented(counter);
    }
    
    // View function
    function getCounter() external view returns (uint256) {
        return counter;
    }
}

