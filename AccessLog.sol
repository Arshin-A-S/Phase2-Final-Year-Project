// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AccessLog {
    event AccessLogged(string username, string fileId, string action, bool granted, string reason, uint256 timestamp);

    function logAccess(string memory _username, string memory _fileId, string memory _action, bool _granted, string memory _reason) public {
        emit AccessLogged(_username, _fileId, _action, _granted, _reason, block.timestamp);
    }
}