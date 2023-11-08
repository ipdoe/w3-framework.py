from w3f import ROOT_PATH
from w3f.lib.metadata import Metadata

class MongMetadata(Metadata):
    _DAT = ROOT_PATH / "dat/mong"
    COLLECTION_NAME = "MONGS NFT"
    CONTRACT = "0xb4a7d131436ed8EC06aD696FA3BF8d23C0aB3Acf"
    MAX_SUPPLY = 6969
    _ID_OFFSET = 1000000

    def __init__(self) -> None:
        super().__init__()

    def get_rarity(self, id):
        return self._m_metadata[str(id)]['open_rarity_rank']