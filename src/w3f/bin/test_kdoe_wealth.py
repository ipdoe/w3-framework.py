from w3f.lib import bots

services = bots.Services()

print(services.get_wealth("0x0DF9dF231Ab1457fB3c259E13ae5408931BcbE2c").to_str())