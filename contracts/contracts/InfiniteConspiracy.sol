// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title InfiniteConspiracy
 * @dev Blockchain detective game with bounty mechanics and player statistics
 */
contract InfiniteConspiracy is AccessControl, ReentrancyGuard {
    
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");
    
    uint256 public constant INSCRIPTION_FEE = 10 ether; // 10 KSM
    uint256 public constant BASE_SUBMISSION_FEE = 1 ether; // 1 KSM
    
    struct Mystery {
        bytes32 mysteryId;
        bytes32 answerHash;
        bytes32 proofHash;
        uint256 bountyPool;
        uint256 createdAt;
        uint256 expiresAt;
        uint8 difficulty;
        bool solved;
        address solver;
        bool proofRevealed;
        string proofData;
    }
    
    struct PlayerStats {
        bool inscribed;
        uint256 mysteriesSolved;
        uint256 totalBountyWon;
        uint256 totalSubmissions;
        uint256 reputation;
        uint256 inscriptionTime;
    }
    
    mapping(bytes32 => Mystery) public mysteries;
    mapping(address => PlayerStats) public playerStats;
    mapping(bytes32 => uint256) public mysterySubmissionCount;
    mapping(address => mapping(bytes32 => uint256)) public playerMysterySubmissions;
    
    bytes32[] public activeMysteries;
    bytes32[] public solvedMysteries;
    address[] public leaderboard;
    
    uint256 public treasuryBalance;
    
    event PlayerInscribed(address indexed player, uint256 poolContribution);
    event MysteryCreated(bytes32 indexed mysteryId, uint256 bounty);
    event AnswerSubmitted(bytes32 indexed mysteryId, address indexed player, uint256 cost);
    event MysterySolved(bytes32 indexed mysteryId, address indexed solver, uint256 bounty);
    event ProofRevealed(bytes32 indexed mysteryId, string proof);
    
    constructor(address oracle) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ORACLE_ROLE, oracle);
    }
    
    // ============ PLAYER INSCRIPTION ============
    
    function inscribePlayer() external payable nonReentrant {
        require(msg.value >= INSCRIPTION_FEE, "Insufficient fee");
        require(!playerStats[msg.sender].inscribed, "Already inscribed");
        
        playerStats[msg.sender] = PlayerStats({
            inscribed: true,
            mysteriesSolved: 0,
            totalBountyWon: 0,
            totalSubmissions: 0,
            reputation: 0,
            inscriptionTime: block.timestamp
        });
        
        leaderboard.push(msg.sender);
        
        // Split inscription: 50% treasury, 50% to active mystery pools
        uint256 halfFee = msg.value / 2;
        treasuryBalance += halfFee;
        
        if (activeMysteries.length > 0) {
            uint256 perMystery = halfFee / activeMysteries.length;
            for (uint i = 0; i < activeMysteries.length; i++) {
                mysteries[activeMysteries[i]].bountyPool += perMystery;
            }
        } else {
            // No active mysteries, add to treasury
            treasuryBalance += halfFee;
        }
        
        emit PlayerInscribed(msg.sender, halfFee);
    }
    
    // ============ ORACLE FUNCTIONS ============
    
    function createMystery(
        bytes32 mysteryId,
        bytes32 answerHash,
        bytes32 proofHash,
        uint256 duration,
        uint8 difficulty
    ) external onlyRole(ORACLE_ROLE) payable {
        require(mysteries[mysteryId].mysteryId == bytes32(0), "Exists");
        
        mysteries[mysteryId] = Mystery({
            mysteryId: mysteryId,
            answerHash: answerHash,
            proofHash: proofHash,
            bountyPool: msg.value,
            createdAt: block.timestamp,
            expiresAt: block.timestamp + duration,
            difficulty: difficulty,
            solved: false,
            solver: address(0),
            proofRevealed: false,
            proofData: ""
        });
        
        activeMysteries.push(mysteryId);
        emit MysteryCreated(mysteryId, msg.value);
    }
    
    function revealProof(bytes32 mysteryId, string calldata proof) 
        external 
        onlyRole(ORACLE_ROLE) 
    {
        Mystery storage mystery = mysteries[mysteryId];
        require(block.timestamp > mystery.expiresAt || mystery.solved, "Not ready");
        require(!mystery.proofRevealed, "Already revealed");
        require(keccak256(bytes(proof)) == mystery.proofHash, "Invalid proof");
        
        mystery.proofRevealed = true;
        mystery.proofData = proof;
        emit ProofRevealed(mysteryId, proof);
    }
    
    // ============ PLAYER SUBMISSION ============
    
    function submitAnswer(bytes32 mysteryId, string calldata answer) 
        external 
        payable 
        nonReentrant 
    {
        Mystery storage mystery = mysteries[mysteryId];
        PlayerStats storage stats = playerStats[msg.sender];
        
        require(stats.inscribed, "Not inscribed");
        require(!mystery.solved, "Solved");
        require(block.timestamp < mystery.expiresAt, "Expired");
        
        // Quadratic cost
        uint256 submissions = playerMysterySubmissions[msg.sender][mysteryId];
        uint256 required = BASE_SUBMISSION_FEE + (submissions ** 2) * 1 ether;
        require(msg.value >= required, "Insufficient fee");
        
        mysterySubmissionCount[mysteryId]++;
        playerMysterySubmissions[msg.sender][mysteryId]++;
        stats.totalSubmissions++;
        mystery.bountyPool += msg.value;
        
        emit AnswerSubmitted(mysteryId, msg.sender, msg.value);
        
        // Check answer
        bytes32 hash = keccak256(abi.encodePacked(_toLower(answer)));
        if (hash == mystery.answerHash) {
            _solveMystery(mysteryId, msg.sender);
        }
    }
    
    function _solveMystery(bytes32 mysteryId, address solver) internal {
        Mystery storage mystery = mysteries[mysteryId];
        PlayerStats storage stats = playerStats[solver];
        
        mystery.solved = true;
        mystery.solver = solver;
        
        stats.mysteriesSolved++;
        stats.totalBountyWon += mystery.bountyPool;
        stats.reputation += 100 * mystery.difficulty;
        
        uint256 bounty = mystery.bountyPool;
        mystery.bountyPool = 0;
        
        (bool success, ) = solver.call{value: bounty}("");
        require(success, "Transfer failed");
        
        _removeFromActive(mysteryId);
        solvedMysteries.push(mysteryId);
        _updateLeaderboard(solver);
        
        emit MysterySolved(mysteryId, solver, bounty);
    }
    
    // ============ VIEW FUNCTIONS ============
    
    function getLeaderboard(uint256 limit) external view returns (
        address[] memory players,
        uint256[] memory reputations,
        uint256[] memory solvedCounts
    ) {
        uint256 count = limit > leaderboard.length ? leaderboard.length : limit;
        players = new address[](count);
        reputations = new uint256[](count);
        solvedCounts = new uint256[](count);
        
        for (uint i = 0; i < count; i++) {
            address player = leaderboard[i];
            players[i] = player;
            reputations[i] = playerStats[player].reputation;
            solvedCounts[i] = playerStats[player].mysteriesSolved;
        }
    }
    
    function getPlayerStats(address player) external view returns (PlayerStats memory) {
        return playerStats[player];
    }
    
    function getMystery(bytes32 mysteryId) external view returns (Mystery memory) {
        return mysteries[mysteryId];
    }
    
    function getActiveMysteries() external view returns (bytes32[] memory) {
        return activeMysteries;
    }
    
    function getSubmissionCost(address player, bytes32 mysteryId) 
        external 
        view 
        returns (uint256) 
    {
        uint256 submissions = playerMysterySubmissions[player][mysteryId];
        return BASE_SUBMISSION_FEE + (submissions ** 2) * 1 ether;
    }
    
    // ============ INTERNAL ============
    
    function _removeFromActive(bytes32 mysteryId) internal {
        for (uint i = 0; i < activeMysteries.length; i++) {
            if (activeMysteries[i] == mysteryId) {
                activeMysteries[i] = activeMysteries[activeMysteries.length - 1];
                activeMysteries.pop();
                break;
            }
        }
    }
    
    function _updateLeaderboard(address player) internal {
        // Simplified bubble sort for demo
        for (uint i = 0; i < leaderboard.length - 1; i++) {
            if (playerStats[leaderboard[i]].reputation < playerStats[leaderboard[i+1]].reputation) {
                address temp = leaderboard[i];
                leaderboard[i] = leaderboard[i+1];
                leaderboard[i+1] = temp;
            }
        }
    }
    
    function _toLower(string memory str) internal pure returns (string memory) {
        bytes memory bStr = bytes(str);
        bytes memory bLower = new bytes(bStr.length);
        for (uint i = 0; i < bStr.length; i++) {
            if ((uint8(bStr[i]) >= 65) && (uint8(bStr[i]) <= 90)) {
                bLower[i] = bytes1(uint8(bStr[i]) + 32);
            } else {
                bLower[i] = bStr[i];
            }
        }
        return string(bLower);
    }
}

