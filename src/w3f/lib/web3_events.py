from hexbytes import HexBytes


class UniV2Swap:
    def __init__(self, decoded_swap_event: dict) -> None:
        # self._decoded_swap_event = decoded_swap_event
        self.sender: str = decoded_swap_event['args']['sender']
        self.to: str = decoded_swap_event['args']['to']
        self.amountIn: int = decoded_swap_event['args']['amount0In']
        self.amountOut: int = -decoded_swap_event['args']['amount1Out']
        if not self.amountIn:
            self.amountIn = decoded_swap_event['args']['amount1In']
            self.amountOut = -decoded_swap_event['args']['amount0Out']
        self.tx_hash: str = decoded_swap_event['transactionHash']
        if isinstance(self.tx_hash, HexBytes):
            self.tx_hash = self.tx_hash.hex()

    def __str__(self) -> str:
        return f'{self.__dict__}'


class UniV3Swap:
    def __init__(self, decoded_swap_event: dict) -> None:
        self.sender: str = decoded_swap_event['args']['sender']
        self.recipient: str = decoded_swap_event['args']['recipient']
        self.amount0: int = decoded_swap_event['args']['amount0']
        self.amount1: int = decoded_swap_event['args']['amount1']
        self.sqrtPriceX96: int = decoded_swap_event['args']['sqrtPriceX96']
        self.liquidity: int = decoded_swap_event['args']['liquidity']
        self.tick: int = decoded_swap_event['args']['tick']
        self.tx_addr: str = decoded_swap_event['address']
        self.tx_hash: str = decoded_swap_event['transactionHash']
        if isinstance(self.tx_hash, HexBytes):
            self.tx_hash = self.tx_hash.hex()

    def __str__(self) -> str:
        return f'{self.__dict__}'
