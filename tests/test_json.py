import shutil
import pytest
from pathlib import Path
from w3f.lib import json

from . import TEST_DATA

TEST_DIR = TEST_DATA / "tmp" / __name__


@pytest.fixture()
def cleanup():
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    yield
    shutil.rmtree(TEST_DIR)


def test__load():
    j = json.load(TEST_DATA / "bnb-eth_tx.json")
    assert j["address"] == "0x3537c4532ebf720ff130ae6a5a92dc39de31a4d8"


def test__loads():
    j = json.loads(r'{"a": "b", "c": "d"}')
    assert j["c"] == "d"


def test__dumps():
    j = {"a": "b", "c": "d"}
    s = '{\n  "a": "b",\n  "c": "d"\n}'
    assert json.dumps(j) == s


def test__dump(cleanup):
    j = {"a": "b", "c": "d"}
    path = TEST_DIR / "my_json.json"
    json.dump(j, path)
    j2 = json.load(path)
    assert j == j2
