
import w3f
import w3f.lib.json


def _get_abi(basename: str):
    return w3f.lib.json.load((w3f.ROOT_PATH / "lib/contracts/abi" / basename).with_suffix(".json"))
