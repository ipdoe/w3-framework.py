from hexbytes import HexBytes


class UniV2Swap:
    def __init__(self, decoded_swap_event: dict) -> None:
        # self._decoded_swap_event = decoded_swap_event
        self.sender: str = decoded_swap_event['args']['sender']
        self.to: str = decoded_swap_event['args']['to']
        self.amountIn: int = decoded_swap_event['args']['amount0In']
        self.amountOut: int = decoded_swap_event['args']['amount1Out']
        self._out_idx = 1
        if not self.amountIn:
            self.amountIn = decoded_swap_event['args']['amount1In']
            self.amountOut = decoded_swap_event['args']['amount0Out']
            self._out_idx = 0
        self.tx_hash: str = decoded_swap_event['transactionHash']
        if isinstance(self.tx_hash, HexBytes):
            self.tx_hash = self.tx_hash.hex()

    def out_idx(self):
        return self._out_idx

    def in_idx(self):
        return 1 - self._out_idx

    def __str__(self) -> str:
        return f'{self.__dict__}'
