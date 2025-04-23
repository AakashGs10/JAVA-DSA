// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BlockchainLedger {
    address public owner;
    uint256 public feePercent = 5;
    uint256 public rewardPercent = 5;
    uint256 public discountThreshold = 100;
    uint256 public trustThreshold = 10;

    constructor() {
        owner = msg.sender;
    }

    struct Transactor {
        uint256 totalSent;
        uint256 totalReceived;
        bool eligibleForDiscount;
    }

    struct Validator {
        uint256 stakedAmount;
        uint256 totalValidated;
        uint256 trustScore;
        bool active;
        uint256 rewardBalance;
    }

    struct Transaction {
        address sender;
        address receiver;
        uint256 amount;
        address validator;
        bool validated;
    }

    mapping(address => Transactor) public transactors;
    mapping(address => Validator) public validators;
    Transaction[] public transactions;

    modifier onlyValidator() {
        require(validators[msg.sender].active, "Not an active validator.");
        _;
    }

    function registerValidator() external payable {
        require(msg.value > 0, "Must pledge ETH to register.");
        validators[msg.sender] = Validator({
            stakedAmount: msg.value,
            totalValidated: 0,
            trustScore: 0,
            active: true,
            rewardBalance: 0
        });
    }

    function submitTransaction(address receiver, uint256 amount) external payable {
        require(amount > 0, "Amount must be positive.");
        uint256 fee = (amount * feePercent) / 1000;

        if (transactors[msg.sender].eligibleForDiscount) {
            fee = fee / 2;
        }

        require(msg.value == amount + fee, "Incorrect amount + fee sent.");
        address selectedValidator = pickValidator(amount);
        require(selectedValidator != address(0), "No validators available.");

        transactions.push(Transaction({
            sender: msg.sender,
            receiver: receiver,
            amount: amount,
            validator: selectedValidator,
            validated: false
        }));

        transactors[msg.sender].totalSent += amount;
        transactors[receiver].totalReceived += amount;

        if (transactors[msg.sender].totalSent >= discountThreshold) {
            transactors[msg.sender].eligibleForDiscount = true;
        }

        validators[selectedValidator].rewardBalance += (amount * rewardPercent) / 1000;
    }

    function validateTransaction(uint256 txId) external onlyValidator {
        require(txId < transactions.length, "Invalid transaction ID.");
        Transaction storage txObj = transactions[txId];
        require(txObj.validator == msg.sender, "You are not assigned to this transaction.");
        require(!txObj.validated, "Already validated.");

        txObj.validated = true;
        validators[msg.sender].trustScore += 1;
        validators[msg.sender].totalValidated += txObj.amount;
    }

    function claimRewards() external onlyValidator {
        uint256 reward = validators[msg.sender].rewardBalance;
        require(reward > 0, "No rewards available.");
        validators[msg.sender].rewardBalance = 0;
        payable(msg.sender).transfer(reward);
    }

    function redeemStake() external onlyValidator {
        Validator storage val = validators[msg.sender];
        require(val.trustScore >= trustThreshold, "Trust score too low to redeem.");
        uint256 staked = val.stakedAmount;
        val.stakedAmount = 0;
        val.active = false;
        payable(msg.sender).transfer(staked);
    }

    function pickValidator(uint256 amount) internal view returns (address) {
        address bestValidator = address(0);
        uint256 minDifference = type(uint256).max;

        for (uint i = 0; i < transactions.length; i++) {
            address candidate = transactions[i].validator;
            if (!validators[candidate].active) continue;
            uint256 validated = validators[candidate].totalValidated;
            uint256 diff = (validated > amount) ? validated - amount : amount - validated;
            if (diff < minDifference) {
                minDifference = diff;
                bestValidator = candidate;
            }
        }
        return bestValidator;
    }

    function getTransactionCount() public view returns (uint256) {
        return transactions.length;
    }

    function getTransaction(uint256 txId) public view returns (
        address, address, uint256, address, bool
    ) {
        Transaction memory txObj = transactions[txId];
        return (txObj.sender, txObj.receiver, txObj.amount, txObj.validator, txObj.validated);
    }
}
