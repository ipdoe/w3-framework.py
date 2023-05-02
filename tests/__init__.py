import inspect, pathlib

_TEST_ROOT = pathlib.Path(inspect.getfile(inspect.currentframe())).parent
TEST_DATA = _TEST_ROOT / "dat"