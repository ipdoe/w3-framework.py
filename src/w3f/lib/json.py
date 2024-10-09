from typing import Union

import json as j
from pathlib import Path
import compact_json

from web3._utils.encoding import Web3JsonEncoder


def __get_compact_formatter(indent=2):
    formatter = compact_json.Formatter()
    formatter.indent_spaces = indent
    formatter.max_inline_length = 150
    formatter.max_inline_complexity = 10
    formatter.json_eol_style = compact_json.EolStyle.LF
    return formatter


def dump(data, target: Path, indent=2, sort_keys=False):
    with open(target, 'w') as f:
        j.dump(data, f, indent=indent, cls=Web3JsonEncoder)


def dumps(data, indent=2, sort_keys=False):
    return j.dumps(data, indent=indent, sort_keys=sort_keys, cls=Web3JsonEncoder)


def load(path: Union[Path, str]):
    with open(path, 'r') as f:
        return j.load(f)


def loads(data):
    return j.loads(data)


def pprint(data, indent=2, sort_keys=False, flush=False):
    try:
        print(dumps_compact(data, indent))
    except Exception:
        print(dumps(data, indent, sort_keys), flush=flush)


def dump_compact(data, target: Union[Path, str], indent=2):
    target = Path(target).as_posix()
    return __get_compact_formatter(indent).dump(data, target, True)


def dumps_compact(data, indent=2):
    return __get_compact_formatter(indent).serialize(data)
