from w3f.lib.mong_metadata import MongMetadata
from w3f import ROOT_PATH

def test__path__ok():
    assert MongMetadata._raw_metadata() == ROOT_PATH / "dat/mong/raw_metadata.json"
    assert MongMetadata._metadata() == ROOT_PATH / "dat/mong/metadata.json"
    MongMetadata.get_metadata()

def test__read_attributes_from_raw_metadata__ok():
    attributes = MongMetadata.read_attributes_from_raw_metadata()
    for a in attributes:
        trait_type = attributes[a]
        sum = 0
        for t in trait_type:
            sum += trait_type[t]
        assert sum == MongMetadata.MAX_SUPPLY
