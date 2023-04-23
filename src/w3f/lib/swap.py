
import decimal
from web3 import Web3
from w3f.lib import eth_event_socket

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
    def __init__(self, abi, name, address, tokens: list[SwapToken], buy_idx=1, buy_char='🧩') -> None:
        self.abi = abi
        self.name = name
        self.address = address
        self.tokens = tokens
        self.buy_idx = buy_idx
        self.buy_token = self.tokens[self.buy_idx]
        self.sell_token = self.tokens[1 - self.buy_idx]
        self.buy_char = buy_char

    @staticmethod
    def green_red(char, usd_val):
        return char * max(1, len(str(int(usd_val))))

    def is_buy(self, swap_data: eth_event_socket.SwapData):
        return swap_data.out_t.id == self.buy_idx

    def buy_sell_msg(self, swap_data: eth_event_socket.SwapData, usd_val):
        usd_msg = f" (${usd_val:,.2f})" if usd_val > 0.0 else ""

        if self.is_buy(swap_data):
            return f"{Swap.green_red(self.buy_char, usd_val)}\n{self.buy_msg(swap_data, usd_msg)}\n" \
                   f"addr: {swap_data.addr_link},  Tx: {swap_data.tx_link}"

        return f"{Swap.green_red('🔴', usd_val)}\n{self.sell_msg(swap_data, usd_msg)}\n" \
               f"addr: {swap_data.addr_link},  Tx: {swap_data.tx_link}"

    def buy_msg(self, swap_data: eth_event_socket.SwapData, usd_msg: str):
        return f"In: {self.sell_token.to_string(swap_data.in_t.ammount)}{usd_msg}\n" \
               f"Out: {self.buy_token.to_string(swap_data.out_t.ammount)}"

    def sell_msg(self, swap_data: eth_event_socket.SwapData, usd_msg: str):
        return f"In: {self.buy_token.to_string(swap_data.in_t.ammount)}{usd_msg}\n" \
               f"Out: {self.sell_token.to_string(swap_data.out_t.ammount)}"
