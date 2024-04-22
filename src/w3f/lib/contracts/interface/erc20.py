import pathlib
from w3f.lib.contracts import _get_abi
from w3f.lib.web3 import W3, Contract

ABI = _get_abi("Ierc20")
NAME = pathlib.PurePath(__file__).stem


class Erc20(Contract):
    def __init__(self, w3: W3, address: str) -> None:
        super().__init__(NAME, w3, address, ABI)
        self.name = self.contract.functions.name().call()
        self.symbol = self.contract.functions.symbol().call()
        self.decimals = self.contract.functions.decimals().call()
        self._to_float = 10 ** self.decimals

    def to_float(self, amount: int) -> float:
        return amount / self._to_float

    def total_supply(self) -> int:
        return self.contract.functions.totalSupply().call()

    def balance_of(self, address: str) -> int:
        return self.contract.functions.balanceOf(address).call()

    def transfer(self, recipient: str, amount: int) -> bool:
        return self.contract.functions.transfer(recipient, amount).call()

    def allowance(self, owner: str, spender: str) -> int:
        """Returns the remaining number of tokens that spender will be allowed to spend on behalf of owner
            through transferFrom. This is zero by default.
        """
        return self.contract.functions.allowance(owner, spender).call()

    def approve(self, spender: str, amount: int) -> bool:
        return self.contract.functions.approve(spender, amount).call()

    def transfer_from(self, sender: str, recipient: str, amount: int) -> bool:
        return self.contract.functions.transferFrom(sender, recipient, amount).call()

    def balance_of_float(self, address: str) -> float:
        return self._to_float(self.balance_of(address))
