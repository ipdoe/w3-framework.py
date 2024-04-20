
from eth_typing import HexStr
from hexbytes import HexBytes
from typing import List
from web3 import Web3


class FungibleToken:
    def __init__(self, tracker, unit, decimals=2) -> None:
        self.tracker = tracker
        self.unit = unit
        self.decimals = decimals
        self.ammount = 0.0

    def set_ammount(self, amount: int):
        self.ammount = float(Web3.from_wei(amount, self.unit))
        return self

    def __str__(self) -> str:
        return f'{self.ammount:,.{self.decimals}f} {self.tracker}'


class FungibleTokenSwap:
    def __init__(self, buy_token: FungibleToken, sell_token: FungibleToken) -> None:
        self._buy_token = buy_token
        self._sell_token = sell_token
        self.buy = True

    def set_ammount(self, buy_ammount: int, sell_ammount: int, buy: bool):
        self._buy_token.set_ammount(buy_ammount)
        self._sell_token.set_ammount(sell_ammount)
        self.buy = buy


class BuySellToken:
    @staticmethod
    def _green_red(char, usd_val, divisor):
        return char * max(1, min(int(usd_val) // divisor, 1000))

    def __init__(self, tokens: List[FungibleToken], buy_idx: int, amountIn: list, amountOut: list) -> None:
        sell_idx = 1 - buy_idx

        if amountOut[buy_idx]:
            # Buy
            self.buy = True
            self.in_token = tokens[sell_idx]
            self.out_token = tokens[buy_idx]
            self.in_token.set_ammount(amountIn[sell_idx])
            self.out_token.set_ammount(amountOut[buy_idx])
            self.buy_token = self.out_token
            self.sell_token = self.in_token
        else:
            # Sell
            self.buy = False
            self.in_token = tokens[buy_idx]
            self.out_token = tokens[sell_idx]
            self.in_token.set_ammount(amountIn[buy_idx])
            self.out_token.set_ammount(amountOut[sell_idx])
            self.buy_token = self.in_token
            self.sell_token = self.out_token

    def buy_sell_msg(self, oracle_usd_price, buy_char: str, divisor: int, sell_char: str):
        swap_char = buy_char if self.buy else sell_char
        swap_usd_val = self.sell_token.ammount * oracle_usd_price
        token_price_usd = swap_usd_val / self.buy_token.ammount

        usd_msg = f" (${swap_usd_val:,.2f})" if swap_usd_val > 0.0 else ""
        price_msg = f"Price: ${token_price_usd:f}\n" if token_price_usd > 0.0 else ""

        return f"{self._green_red(swap_char, swap_usd_val, divisor)}\n" \
                f"In: {self.in_token}{usd_msg}\n" \
                f"Out: {self.out_token}\n" \
                f"{price_msg}"


class SwapLog:
    def __init__(self, decoded_swap_event: dict) -> None:
        self._decoded_swap_event = decoded_swap_event
        self.sender = decoded_swap_event['args']['sender']
        self.to = decoded_swap_event['args']['to']
        self.amountIn = decoded_swap_event['args']['amount0In']
        self.amountOut = decoded_swap_event['args']['amount1Out']
        if not self.amountIn:
            self.amountIn = decoded_swap_event['args']['amount1In']
            self.amountOut = decoded_swap_event['args']['amount0Out']
        self.tx_hash: HexStr = decoded_swap_event['transactionHash']
        if isinstance(self.tx_hash, HexBytes):
            self.tx_hash = HexStr(self.tx_hash.hex())

    def __str__(self) -> str:
        return f'{self.__dict__}'
