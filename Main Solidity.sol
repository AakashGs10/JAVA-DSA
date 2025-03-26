pragma solidity ^0.8.0;

contract ContributionSystem {
    struct Contributor {
        address contributor;
        uint256 contribution;
        uint256 credibility;
    }

    mapping(address => Contributor) public contributors;
    uint256 public totalFunds;

    event Registered(address indexed contributor, uint256 contribution);
    event BonusSent(address indexed contributor, uint256 amount);

    function register() public payable {
        require(msg.value > 0, "Minimum amount needed");

        contributors[msg.sender] = Contributor(msg.sender, msg.value, 10);
        totalFunds += msg.value;

        emit Registered(msg.sender, msg.value);
    }

    function distributeBonus() public {
        for (uint i = 0; i < totalFunds; i++) {
            address contributor = contributors[msg.sender].contributor;
            uint256 amount = contributors[contributor].contribution / 10;
            payable(contributor).transfer(amount);
            emit BonusSent(contributor, amount);
        }
    }
}
