import discord, asyncio
import telegram as tg
import w3f.lib.logger as log

class Bots:
    def __init__(self, tg: tg.Bot) -> None:
        self.tg = tg

    @staticmethod
    def init_none():
        return Bots(None)

class TgChannel:
    def __init__(self) -> None:
        self.bot = None
        self.chat_id = 0

    def init(self, tg_token: str, chat_id: int, description: str) -> None:
        self.bot = None
        self.chat_id = 0
        bot = None
        try:
            bot = tg.Bot(token=tg_token)
            bot.send_message(chat_id=chat_id, text=" ")
        except tg.error.TelegramError as e:
            # This is the expected error --> OK
            if e.message == 'Message must be non-empty':
                self.chat_id = chat_id
                self.bot = bot
                return
            log.log(f'Failed to initialize tg {description}({chat_id}): {e}. INACTIVE')
        except Exception as e:
            log.log(f'Failed to initialize tg {description}({chat_id}): {e}. INACTIVE')

    def send_text(self, md_msg: str):
        if self.bot is not None:
            try:
                self.bot.send_message(chat_id=self.chat_id, parse_mode=tg.ParseMode.MARKDOWN,
                disable_web_page_preview=True, text=md_msg)
            except Exception as e:
                log.log(f'Failed to send msg to tg({self.chat_id}): {e}')

    def send_with_img(self, md_msg: str):
        if self.bot is not None:
            try:
                self.bot.send_message(chat_id=self.chat_id, parse_mode=tg.ParseMode.MARKDOWN, text=md_msg)
            except Exception as e:
                log.log(f'Failed to send msg to tg({self.chat_id}): {e}')

class DscrdChannel:
    def __init__(self, id: int) -> None:
        self.id = id
        self.chan = None

    def set_channel(self, client):
        try:
            self.chan = client.get_channel(self.id)
            log.log(f'Channel OK: {self.chan}')
        except:
            pass

    async def send(self, message):
        if self.chan is not None:
            try:
                if type(message) is discord.Embed:
                    await self.chan.send(embed=message)
                else:
                    await self.chan.send(message)
            except Exception as e:
                log.log(f'Failed to send embed to discord {self.chan}: {e}')

class DscrdChannels:
    def __init__(self) -> None:
        self.doe_nft_listing = DscrdChannel(0)
        self.doe_nft_sales = DscrdChannel(0)
        self.doe_nft_floor = DscrdChannel(0)
        self.doe_token_buys = DscrdChannel(0)
        self.ipdoe_dbg = DscrdChannel(0)
        self.ipdoe_nft = DscrdChannel(0)
        self.ipdoe_nft_sales = DscrdChannel(0)
        self.ipdoe_nft_listings = DscrdChannel(0)
        self.ipdoe_nft_offers = DscrdChannel(0)
        self.ipdoe_swaps = DscrdChannel(0)

    def init_channels(self, client):
        self.doe_nft_listing.set_channel(client)
        self.doe_nft_sales.set_channel(client)
        self.doe_nft_floor.set_channel(client)
        self.doe_token_buys.set_channel(client)
        self.ipdoe_dbg.set_channel(client)
        self.ipdoe_nft.set_channel(client)
        self.ipdoe_nft_sales.set_channel(client)
        self.ipdoe_nft_listings.set_channel(client)
        self.ipdoe_nft_offers.set_channel(client)
        self.ipdoe_swaps.set_channel(client)