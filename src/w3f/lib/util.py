import json
from pathlib import Path
from web3 import Web3

def dump_json(target: Path, data: dict, indent=None):
    with open(target, 'w') as o:
        if indent is None:
            json.dump(data, o)
        else:
            o.write(json.dumps(data, indent=indent))

def load_json(path: Path):
    with open(path, 'r') as f:
        return json.load(f)

def to_json_str(d: dict):
    try:
        return json.dumps(d, indent=2)
    except:
        return ""

def web3_pretty_json(web3_obj, indent=2):
    return json.dumps(json.loads(Web3.to_json(web3_obj)), indent=indent)

def short_hex(hex: str, chars=8):
    return hex[0:chars]