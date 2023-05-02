
import decimal
from web3 import Web3
from w3f.lib import eth_event_socket

class SwapToken:
    def __init__(self, tracker, unit, decimals) -> None:
        self.tracker = tracker
        self.unit = unit
        self.decimals = decimals
        self.ammount = 0.0

    def set_ammount(self, amount: decimal.Decimal):
        self.ammount = float(Web3.fromWei(amount, self.unit))

    def to_string(self):
        return f'{self.ammount:,.{self.decimals}f} {self.tracker}'


class Swap:
    def __init__(self, abi, name, address, tokens: list[SwapToken],
                 buy_idx, chain = eth_event_socket.Chain.ETH, buy_char='🟢') -> None:
        self.abi = abi
        self.name = name
        self.address = address
        self.tokens = tokens
        self.chain = chain
        self.buy_idx = buy_idx
        self.buy_token: SwapToken = self.tokens[self.buy_idx]
        self.sell_token: SwapToken = self.tokens[1 - self.buy_idx]
        self.buy_char = buy_char

    @staticmethod
    def _green_red(char, usd_val):
        return char * max(1, len(str(int(usd_val))))

    def is_buy(self, swap_data: eth_event_socket.SwapData):
        return swap_data.ammounts.out_idx == self.buy_idx

    def buy_sell_msg(self, swap_data: eth_event_socket.SwapData, oracle_usd_price):
        # SELL
        self.buy_token.set_ammount(swap_data.ammounts.in_a)
        self.sell_token.set_ammount(swap_data.ammounts.out_a)
        usd_val = self.sell_token.ammount * oracle_usd_price
        usd_msg = f" (${usd_val:,.2f})" if usd_val > 0.0 else ""
        swap_char = '🔴'
        msg = self._sell_msg(usd_msg)

        # buy
        if self.is_buy(swap_data):
            self.buy_token.set_ammount(swap_data.ammounts.out_a)
            self.sell_token.set_ammount(swap_data.ammounts.in_a)
            usd_val = self.sell_token.ammount * oracle_usd_price
            usd_msg = f" (${usd_val:,.2f})" if usd_val > 0.0 else ""
            swap_char = self.buy_char
            msg = self._buy_msg(usd_msg)

        return f"{Swap._green_red(swap_char, usd_val)}\n{msg}\n" \
               f"addr: {swap_data.addr_link},  Tx: {swap_data.tx_link}"

    def _buy_msg(self, usd_msg: str):
        return f"In: {self.sell_token.to_string()}{usd_msg}\n" \
               f"Out: {self.buy_token.to_string()}"

    def _sell_msg(self, usd_msg: str):
        return f"In: {self.buy_token.to_string()}{usd_msg}\n" \
               f"Out: {self.sell_token.to_string()}"

