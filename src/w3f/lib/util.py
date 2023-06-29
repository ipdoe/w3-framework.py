import json
from pathlib import Path

def dump_json(target: Path, data: dict, indent=None):
    with open(target, 'w') as o:
        if indent is None:
            json.dump(data, o)
        else:
            o.write(json.dumps(data, indent=indent))

def load_json(path: Path):
    with open(path, 'r') as f:
        return json.load(f)