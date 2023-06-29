from w3f import ROOT_PATH
from w3f.lib.util import dump_json, load_json
from open_rarity import Collection, Token, RarityRanker, TokenMetadata, StringAttribute
from open_rarity.models.token_identifier import EVMContractTokenIdentifier
from open_rarity.models.token_standard import TokenStandard

class Metadata:
    _DAT = ROOT_PATH / "dat/mong"
    COLLECTION_NAME = ""
    CONTRACT = ""
    MAX_SUPPLY = 0

    _METADATA = _DAT / "raw_metadata.json"
    _RANKED_METADATA = _DAT / "ranked_metadata.json"
    _RANKED_METADATA_PRETTY = _DAT / "ranked_metadata_pretty.json"
    _ATTRIBUTES = _DAT / "attributes_histogram.json"

    class Attributes(list):
        def has(self, trait, value):
            if {"trait_type": trait, "value": value} in self:
                return True
            return False

        def to_open_rarity(self):
            open_rarity_attr = {}
            for trait in self:
                open_rarity_attr[trait["trait_type"]] = StringAttribute(name=trait["trait_type"], value=trait["value"])
            return open_rarity_attr


    def __init__(self) -> None:
        self._metadata = self.get_metadata()

    @classmethod
    def get_raw(cls) -> dict:
        return load_json(cls._METADATA)

    @classmethod
    def get_metadata(cls) -> dict:
        return load_json(cls._RANKED_METADATA)

    @classmethod
    def _attr_count(cls, asset_attributes: dict):
        trait_cnt = 0
        for a in asset_attributes:
            if a["value"] != "None":
                trait_cnt += 1
        return trait_cnt


    @classmethod
    def read_attributes_from_raw_metadata(cls) -> dict:
        raw_metadata = cls.get_raw()
        all_attributes = {}
        for id in raw_metadata:
            asset_attributes = raw_metadata[id]["attributes"]
            asset_attributes.append({"trait_type": "trait_count", "value": cls._attr_count(asset_attributes)})

            for trait in asset_attributes:
                all_attributes.setdefault(trait["trait_type"], {trait["value"]: 0})
                all_attributes[trait["trait_type"]].setdefault(trait["value"], 0)
                all_attributes[trait["trait_type"]][trait["value"]] += 1

        # Sort
        for attribute in all_attributes:
            attr = dict(sorted(all_attributes[attribute].items(), key=lambda item: item[1]))
            all_attributes[attribute] = attr

        return all_attributes

    @classmethod
    def dump_attributes(cls):
        dump_json(cls._ATTRIBUTES, cls.read_attributes_from_raw_metadata(), 2)

    @classmethod
    def get_attributes(cls) -> dict:
        return load_json(cls._ATTRIBUTES)

    @classmethod
    def _open_rarity_token(cls, id: int, attributes: dict):
        return Token(
            token_identifier=EVMContractTokenIdentifier(contract_address=cls.CONTRACT, token_id=int(id)),
            token_standard=TokenStandard.ERC721,
            metadata=TokenMetadata(string_attributes=attributes)
        )

    @classmethod
    def calculate_open_rarity(cls):
        metadata = cls.get_raw()
        tokens = []
        for id in metadata:
            try:
                tokens.append(
                    cls._open_rarity_token(int(id), Metadata.Attributes(metadata[id]["attributes"]).to_open_rarity())
                )
            except KeyError:
                pass
        rarity_list = RarityRanker.rank_collection(collection=Collection(name=cls.COLLECTION_NAME, tokens=tokens))
        for nft in rarity_list:
            id = str(nft.token.token_identifier.token_id)
            nft.rank
            metadata[id]["open_rarity_rank"] = nft.rank
            metadata[id]["open_rarity_score"] = nft.score
        return metadata

    @classmethod
    def dump_open_rarity(cls):
        metadata = cls.calculate_open_rarity()
        dump_json(cls._RANKED_METADATA, metadata)
        dump_json(cls._RANKED_METADATA_PRETTY, metadata, indent=2)
