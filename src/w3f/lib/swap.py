from eth_typing import HexStr
from typing import List, Tuple, Union
from web3.types import TxData

from w3f.lib.contracts.interface.erc20 import Erc20
from w3f.lib.contracts.interface.uni_v3 import UniV3
from w3f.lib.network import Explorer
from w3f.lib.util import short_hex
from w3f.lib.web3 import W3
from w3f.lib.web3_events import UniV3Swap


class Token:
    @staticmethod
    def create_tokens(erc20_tokens: Tuple[Erc20, Erc20], amounts: Tuple[float, float]):
        return (Token(erc20_tokens[0], amounts[0]),
                Token(erc20_tokens[1], amounts[1]))

    def __init__(self, token: Erc20, amount: float, precision=0) -> None:
        self.amount = amount
        self.symbol = token.symbol
        self.precision = precision

    def __float__(self):
        return abs(self.amount)

    def __str__(self) -> str:
        if self.precision:
            return f'{self.amount:,.{self.precision}f} {self.symbol}'

        return f'{abs(self.amount)} {self.symbol}'


class SwapObj:
    def __init__(
        self,
        explorer: Explorer,
        swap: UniV3Swap,
        erc20_tokens: Tuple[Erc20, Erc20],
        amounts: Tuple[float, float],
        tx: TxData,
        buy_idx: int,
    ) -> None:
        self._explorer = explorer
        self._swap = swap
        tokens = Token.create_tokens(erc20_tokens, amounts)
        self._buy_token = tokens[buy_idx]
        self._sell_token = tokens[1 - buy_idx]
        self._tx = tx
        self._tx_addr = tx["from"]  # type: ignore

        self._is_buy = False
        self._in_token = tokens[1 - buy_idx]
        self._out_token = tokens[buy_idx]
        if amounts[buy_idx] > 0:
            self._is_buy = True
            self._in_token = tokens[buy_idx]
            self._out_token = tokens[1 - buy_idx]

    @staticmethod
    def _green_red(char, usd_val, divisor):
        return char * max(1, min(abs(int(usd_val)) // divisor, 1000))

    def _addr_msg(self):
        return f"Addr: [{short_hex(self._tx_addr)}]({self._explorer.address(self._tx_addr)})"

    def _tx_msg(self):
        return f"Tx: [{short_hex(self._swap.tx_hash)}]({self._explorer.tx(self._swap.tx_hash)})"

    def _addr_tx_msg(self):
        return f"{self._addr_msg()}, {self._tx_msg()}"

    def trade_msg(
        self, oracle_usd_price, buy_char: str, divisor: int, sell_char: str
    ):
        swap_char = buy_char if self._is_buy else sell_char
        swap_usd_val = abs(self._sell_token.amount * oracle_usd_price)
        token_price_usd = abs(swap_usd_val / self._buy_token.amount)

        usd_msg = f" (${swap_usd_val:,.2f})" if swap_usd_val > 0.0 else ""
        price_msg = f"Price: ${token_price_usd:f}\n" if token_price_usd > 0.0 else ""

        return (
            f"{self._green_red(swap_char, swap_usd_val, divisor)}\n"
            f"In: {self._in_token}{usd_msg}\n"
            f"Out: {self._out_token}\n"
            f"{price_msg}"
            f"{self._addr_tx_msg()}"
        )


class UniV3SwapContract(UniV3):
    def __init__(self, w3: W3, address: str, buy_idx) -> None:
        super().__init__(w3=w3, address=address)
        self.buy_idx = buy_idx

    def process_logs(self, fromBlock=0, toBlock: Union[str, int] = "latest"):
        return self.process_swaps(self.get_all_swaps(fromBlock, toBlock))

    def process_swaps(self, swap_logs: list):
        processed: List[UniV3Swap] = []
        for swap_log in swap_logs:
            processed.append(UniV3Swap(swap_log))
        return processed

    def decode_swap_v3_event(self, swap_event):
        return UniV3Swap(self.decode_event(swap_event))

    def _swap_obj_v3(self, swap_event_or_log: UniV3Swap):
        if not isinstance(swap_event_or_log, UniV3Swap):
            swap_event_or_log = self.decode_swap_v3_event(swap_event_or_log)

        amounts = (self._tokens[0].to_float(swap_event_or_log.amount0),
                   self._tokens[1].to_float(swap_event_or_log.amount1))

        tx = self.w3.w3.eth.get_transaction(HexStr(swap_event_or_log.tx_hash))
        return SwapObj(self.explorer, swap_event_or_log, self._tokens, amounts, tx, self.buy_idx)

    async def wait_swap_v3(self, ws):
        swap = UniV3Swap(await self.wait_event(ws))
        return self._swap_obj_v3(swap)

    async def wait_trade_msg_v3(
        self, ws, oracle_usd_price, buy_char="🟢", divisor=100, sell_char="🔴"
    ):
        swapObj = await self.wait_swap_v3(ws)
        return swapObj.trade_msg(oracle_usd_price, buy_char, divisor, sell_char)
