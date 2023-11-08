from w3f.lib import bots

services = bots.Services()

print(services.get_wealth("0x5dA93cF2d5595Dd68Daed256DFbFF62c7ebBB298").to_str())
