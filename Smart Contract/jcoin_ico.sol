// Jcoin ICO

//Version of compiler
pragma solidity ^0.4.11;

contract jcoin_ico {
    
    // Introducing the maximum number of Jcoins available for sale
    uint public max_jcoins = 1000000;
    
    // Introducing the USD to Jcoins conversion rate
    uint public usd_to_jcoins = 1000;
    
    // Introducing the total number of Jcoins that have been bought by the investor
    uint public total_jcoins_bought = 0;
    
    // Mapping from the investor address to its equity in Jcoins and USD
    mapping(address => uint) equity_jcoins;
    mapping(address => uint) equity_usd;
    
    // Checking if an investor can buy Jcoins
    modifier can_buy_jcoins(uint usd_invested) {
        require (usd_invested * usd_to_jcoins + total_jcoins_bought <= max_jcoins);
        _;
    }
    
    
    // Getting the equity in Jcoins of an investor
    function get_equity_in_jcoins(address investor) external constant returns (uint) {
        return equity_jcoins[investor];
    }
    
    // Getting the equity in USD of an investor
    function get_equity_in_usd(address investor) external constant returns (uint) {
        return equity_usd[investor];
    }
    
    // Buying Jcoins
    function buy_jcoins(address investor, uint usd_invested) external
    can_buy_jcoins(usd_invested) {
        uint jcoins_bought = usd_invested * usd_to_jcoins;
        equity_jcoins[investor] += jcoins_bought;
        equity_usd[investor] = equity_jcoins[investor] / 1000;
        total_jcoins_bought += jcoins_bought;
    }
    
    // Selling jcoins_bought
    function sell_jcoins(address investor, uint jcoins_sold) external {
		equity_jcoins[investor] -= jcoins_sold;
		equity_usd[investor] = equity_jcoins[investor] / 1000;
		total_jcoins_bought -= jcoins_sold;
	}	
}