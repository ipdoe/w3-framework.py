import pathlib
from w3f import ROOT_PATH
from w3f.lib.util import dump_json, load_json
try:
    from open_rarity import Collection, Token, RarityRanker, TokenMetadata, StringAttribute
    from open_rarity.models.token_identifier import EVMContractTokenIdentifier
    from open_rarity.models.token_standard import TokenStandard
except:
    pass

class Metadata:
    NAME = ""
    CONTRACT = ""
    MAX_SUPPLY = 0
    OS_SLUG = ""

    _DAT = pathlib.Path("")

    @classmethod
    def _raw_metadata(cls) -> pathlib.Path:
        return cls._DAT / "raw_metadata.json"

    @classmethod
    def _metadata(cls) -> pathlib.Path:
        return cls._DAT / "metadata.json"

    @classmethod
    def _metadata_pretty(cls) -> pathlib.Path:
        return cls._DAT / "metadata_pretty.json"

    @classmethod
    def _nft_types(cls) -> pathlib.Path:
        return cls._DAT / "nft_types.json"

    @classmethod
    def _attributes_hist(cls) -> pathlib.Path:
        return cls._DAT / "attributes_histogram.json"

    class Attributes(list):
        def has(self, trait, value):
            if {"trait_type": trait, "value": value} in self:
                return True
            return False

        def get(self, trait):
            for attribute in self:
                if attribute["trait_type"] == trait:
                    return attribute["value"]
            return ""

        def to_open_rarity(self):
            open_rarity_attr = {}
            for trait in self:
                open_rarity_attr[trait["trait_type"]] = StringAttribute(name=trait["trait_type"], value=trait["value"])
            return open_rarity_attr

    def __init__(self) -> None:
        self._m_metadata = self.get_metadata()

    def get_rarity(self, id):
        return self._m_metadata[str(id)]['rarity_rank']

    def get_type(self, id):
        return self._m_metadata[str(id)]['type']

    def get_twins(self, id):
        return self._m_metadata[str(id)]['twins']

    @classmethod
    def get_raw(cls) -> dict:
        return load_json(cls._raw_metadata())

    @classmethod
    def get_metadata(cls) -> dict:
        return load_json(cls._metadata())

    @classmethod
    def get_attributes_histogram(cls) -> dict:
        return load_json(cls._attributes_hist())

    @classmethod
    def _attr_count(cls, asset_attributes: dict):
        trait_cnt = 0
        for a in asset_attributes:
            if a["value"] != "None":
                trait_cnt += 1
        return trait_cnt

    @classmethod
    def _append_attributes(cls, id: str, item_metadata: dict, all_attributes: dict):
        asset_attributes: list = item_metadata["attributes"]
        asset_attributes.append({"trait_type": "trait_count", "value": cls._attr_count(asset_attributes)})

        for trait in asset_attributes:
            all_attributes.setdefault(trait["trait_type"], {trait["value"]: 0})
            all_attributes[trait["trait_type"]].setdefault(trait["value"], 0)
            all_attributes[trait["trait_type"]][trait["value"]] += 1

    @classmethod
    def _post_process_attributes(cls, attributes_hist: dict):
        # Sort attributes
        for attribute in attributes_hist:
            attr = dict(sorted(attributes_hist[attribute].items(), key=lambda item: item[1]))
            attributes_hist[attribute] = attr

    @classmethod
    def read_attributes_from_raw_metadata(cls) -> dict:
        raw_metadata = cls.get_raw()
        all_attributes = {}
        for id in raw_metadata:
            cls._append_attributes(id, raw_metadata[id], all_attributes)

        # Sort
        for attribute in all_attributes:
            attr = dict(sorted(all_attributes[attribute].items(), key=lambda item: item[1]))
            all_attributes[attribute] = attr

        return all_attributes

    @classmethod
    def _generate_rarity_list(cls, id: str, metadata, rarity_list: list):
        try:
            attributes = metadata["attributes"]
            rarity_list.append(Token(
                token_identifier=EVMContractTokenIdentifier(contract_address=cls.CONTRACT, token_id=int(id)),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(string_attributes=Metadata.Attributes(attributes).to_open_rarity()))
            )
        except KeyError:
            pass

    @classmethod
    def _append_rarity(cls, metadata: dict, rarity_list: list):
        rarity = RarityRanker.rank_collection(collection=Collection(name=cls.NAME, tokens=rarity_list))
        for nft in rarity:
            id = str(nft.token.token_identifier.token_id)
            metadata[id]["rarity_rank"] = nft.rank
            metadata[id]["rarity_score"] = nft.score

    @classmethod
    def _append_types(cls, id_str: str, item_metadata: dict, types: dict):
        pass

    @classmethod
    def generate_metadata_from_raw(cls):
        metadata = cls.get_raw()
        types = {}
        no_dupes_set = {}
        attributes_hist = {}
        rarity_list = []

        for id in metadata:
            cls._generate_rarity_list(id, metadata[id], rarity_list)
            cls._append_types(id, metadata[id], types, no_dupes_set)
            cls._append_attributes(id, metadata[id], attributes_hist)

        cls._append_rarity(metadata, rarity_list)
        cls._post_process_attributes(attributes_hist)

        return metadata, types, attributes_hist

    @classmethod
    def _dump_nft_types(cls, types):
        dump_json(cls._nft_types(), types)

    @classmethod
    def dump_attributes_histogram(cls):
        _, _, attr_hist = cls.generate_metadata_from_raw()
        dump_json(cls._attributes_hist(), attr_hist, indent=2)

    @classmethod
    def redump(cls):
        metadata, types, attr_hist = cls.generate_metadata_from_raw()
        dump_json(cls._metadata(), metadata)
        dump_json(cls._metadata_pretty(), metadata, indent=2)
        cls._dump_nft_types(types)
        dump_json(cls._attributes_hist(), attr_hist, indent=2)


class DoeMetadata(Metadata):
    NAME = "Dogs of Elon"
    CONTRACT = "0xD8CDB4b17a741DC7c6A57A650974CD2Eba544Ff7"
    MAX_SUPPLY = 9997
    OS_SLUG = "dogs-of-elon"
    _DAT = ROOT_PATH / "dat/doe"

    @classmethod
    def _raw_metadata(cls) -> pathlib.Path:
        return cls._DAT / "raw_metadata.json"

    @classmethod
    def _append_rarity(cls, metadata: dict, rarity_list: list):
        pass

    @classmethod
    def _generate_rarity_list(cls, id: str, metadata, rarity_list: list):
        pass

    @classmethod
    def _post_process_attributes(cls, attributes_hist: dict):
        pass

    @classmethod
    def __get_type(cls, raw_types, id):
        if id > cls.MAX_SUPPLY:
            return 'none'
        if id in raw_types['elons']:
            return 'elon'
        if id in raw_types['aliens']:
            return 'alien'
        if id in raw_types['zombies']:
            return 'zombie'
        if id in raw_types['traitless']:
            return 'traitless'
        return 'doge'

    @classmethod
    def __get_twins(cls, raw_types, id) -> []:
        try:
            return [str(raw_types['twins_dict'][str(id)])]
        except:
            return []

    @classmethod
    def generate_metadata_from_raw(cls):
        raw_metadata = cls.get_raw()
        raw_types = load_json(cls._DAT / "raw_doe_types.json")
        metadata = {}
        attributes_hist = {}

        for item in raw_metadata:
            nft_id = item["nft_id"]
            metadata[nft_id] = {}
            metadata[nft_id]["type"] = cls.__get_type(raw_types, nft_id)
            metadata[nft_id]["twins"] = cls.__get_twins(raw_types, nft_id)
            metadata[nft_id]["rarity_score"] = item["score"]
            metadata[nft_id]["rarity_rank"] = item["rank"]
            metadata[nft_id]["traits_scores"] = item["traits_scores"]

        return metadata, raw_types, attributes_hist