
import decimal
from web3 import Web3

class SwapToken:
    def __init__(self, tracker, unit, decimals) -> None:
        self.tracker = tracker
        self.unit = unit
        self.decimals = decimals
    
    def to_decimal(self, amount: decimal.Decimal):
        return Web3.fromWei(amount, self.unit)
    
    def to_string(self, amount: decimal.Decimal):
        return f'{self.to_decimal(amount):,.{self.decimals}f} {self.tracker}'
        
class Swap:
    def __init__(self, abi, name, address, tokens: list[SwapToken]) -> None:
        self.abi = abi
        self.name = name
        self.address = address
        self.tokens = tokens
        self.buy_token = 1
