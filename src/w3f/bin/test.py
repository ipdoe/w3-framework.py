#!/usr/bin/env python3

from w3f.lib.mong_metadata import MongMetadata
from w3f.lib.util import dump_json
import w3f.lib.logger as log

print(MongMetadata._DAT)
print(MongMetadata._METADATA)
print(MongMetadata.COLLECTION_NAME)
print(MongMetadata.CONTRACT)
print(MongMetadata.MAX_SUPPLY)

ranked = MongMetadata.calculate_open_rarity()
# log.log_json(ranked["5555"])

MongMetadata.dump_open_rarity()
MongMetadata.dump_attributes()