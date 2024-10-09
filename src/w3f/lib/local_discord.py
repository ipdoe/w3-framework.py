from w3f.lib import bots
import w3f.lib.logger as log

class DiscordChannels:
    @staticmethod
    def create_chans(ids):
        id_list = []
        try:
            id_list.extend(ids) # Fails if single item
        except Exception:
            id_list.append(ids)
        return [bots.DscrdChannel(id) for id in id_list]


    def __init__(self, buys_id=0, listings_id=0, other_id=0, debug_id=0) -> None:
        self.buys = self.create_chans(buys_id)
        self.listings = self.create_chans(listings_id)
        self.other = self.create_chans(other_id)
        self.debug = self.create_chans(debug_id)

    def init_channels(self, client):
        try:
            for ch in self.buys: ch.set_channel(client)
            for ch in self.listings: ch.set_channel(client)
            for ch in self.other: ch.set_channel(client)
            for ch in self.debug: ch.set_channel(client)
        except Exception as e:
            log.log("Failed to setup all channels: " + str(e))

    def init_with_hidden_details(self, client, buys_id=0, listings_id=0, other_id=0, debug_id=0):
        try:
            self.buys = self.create_chans(buys_id)
            self.listings = self.create_chans(listings_id)
            self.other = self.create_chans(other_id)
            self.debug = self.create_chans(debug_id)

            self.init_channels(client)
        except Exception as e:
            log.log("Failed to setup all channels: " + str(e))

    @staticmethod
    async def __send(channel_list, embed):
        try:
            len(channel_list)
        except Exception:
            return await channel_list.send(embed)  # single item

        # list
        msg_sent = True
        for ch in channel_list:
            msg_sent = msg_sent and await ch.send(embed)
        return msg_sent

    async def send_buys(self, embed):
        return await self.__send(self.buys, embed)

    async def send_listings(self, embed):
        return await self.__send(self.listings, embed)

    async def send_other(self, embed):
        return await self.__send(self.other, embed)

    async def send_debug(self, embed):
        return await self.__send(self.debug, embed)
