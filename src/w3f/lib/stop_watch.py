import time


class StopWatch:
    def __init__(self) -> None:
        self.__start = time.monotonic()

    def elapsed_s(self):
        return time.monotonic() - self.__start

    def restart(self):
        self.__init__()
