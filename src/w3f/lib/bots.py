from enum import Enum, auto
from typing import List, Dict

import discord
import telegram as tg

import w3f.lib.logger as log
import w3f.hidden_details as hd
from web3 import Web3
from ens import ENS

from telegram.ext import Application, CommandHandler
from telegram.constants import ParseMode

TG_MSG_LIMIT = 4096
DSCRD_MSG_LIMIT = 2000


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

    def init_with_hidden_details(self, client):
        try:
            self.ipdoe_dbg.id = hd.dscrd["ipdoe_dbg"]
            self.ipdoe_nft.id = hd.dscrd["ipdoe_nft"]
            self.ipdoe_nft_sales.id = hd.dscrd["ipdoe_nft_sales"]
            self.ipdoe_nft_listings.id = hd.dscrd["ipdoe_nft_listings"]
            self.ipdoe_nft_offers.id = hd.dscrd["ipdoe_nft_offers"]
            self.ipdoe_swaps.id = hd.dscrd["ipdoe_swaps"]
            self.doe_nft_listing.id = hd.dscrd.get("doe_nft_listing", 0)
            self.doe_nft_sales.id = hd.dscrd.get("doe_nft_sales", 0)
            self.doe_nft_floor.id = hd.dscrd.get("doe_nft_floor", 0)

            self.init_channels(client)
        except Exception as e:
            log.log("Failed to setup all ipdoe channels: " + str(e))


class Services:
    def __init__(self) -> None:
        self.w3 = web3.InfuraEth(hd.infura_key)
        self.w3_bsc = web3.GetBlockBsc(hd.GETBLOCK_KEY)
        self.ens = ENS.from_web3(self.w3.w3)
        self.nft_metadata = doe_nft_data.Metadata()
        self.mong_metadata = mong_metadata.MongMetadata()

    def to_address(self, wallet: str):
        try:
            return Web3.to_checksum_address(wallet)
        except Exception:
            return self.ens.address(wallet)

    def get_wealth(self, wallet):
        return kdoe_wealth.Wealth(
            self.w3, self.w3_bsc, wallet, self.nft_metadata, self.mong_metadata
        )


class DscrdClient(discord.Client):
    def __init__(self, token: str) -> None:
        super().__init__()
        self.ready = False
        self.token = token
        self.chans = DscrdChannels()

    def run(self):
        super().run(self.token)


class Bots:
    def __init__(self, tg: tg.Bot) -> None:
        self.tg = tg

    @staticmethod
    def init_none():
        return Bots(None)


class DscrdBot(discord.Bot):
    def __init__(self, token: str) -> None:
        super().__init__()
        self.ready = False
        self.token = token
        self.chans = DscrdChannels()

    def run(self):
        super().run(self.token)


class WealthDscrdBot(DscrdBot):
    def __init__(self, token: str, services: Services) -> None:
        super().__init__(token)
        self.services = services

    async def event_on_ready(self):
        if not self.ready:
            self.ready = True
            self.services.oracle.create_task()
            self.chans.init_with_hidden_details(self)

    async def cmd_wealth(self, ctx: discord.commands.context.ApplicationContext, wallet):
        try:
            wallet = self.services.to_address(wallet)
            log.log(f"wallet: {wallet}")
            await ctx.respond(f"``{wallet}``", ephemeral=True)
            wealth = self.services.get_wealth(wallet)

            for msg in wealth.to_msg_chunks(DSCRD_MSG_LIMIT - 10):
                await ctx.respond(f"``{msg}``", ephemeral=True)

        except Exception as e:
            log.log(f"Failed: {wallet}\n{e}")
            await ctx.respond("Command failed", ephemeral=True)

    async def cmd_what_time(self, ctx: discord.commands.context.ApplicationContext):
        await ctx.respond("It's KUDOE TIME 🧩!")


class ChatType(Enum):
    DEBUG = auto()
    SALE = auto()
    LISTING = auto()
    ACTIVITY = auto()


class TgBot:
    def __init__(self, token: str, chat_ids: Dict[ChatType, List[int]]) -> None:
        self.app = Application.builder().token(token).build()
        self.app.add_handler(CommandHandler("what_time", self.cmd_what_time))
        self.chat_ids = chat_ids
        # self.app.add_handler(CommandHandler("wealth", self.cmd_wealth))

    async def cmd_what_time(self, update: tg.Update, context) -> None:
        # update.message.chat_id
        await update.message.reply_text("It's DOE TIME 🐶!")  # type: ignore

    async def send_debug(self, text: str, **kwargs):
        for chat_id in self.chat_ids[ChatType.DEBUG]:
            await self.app.updater.bot.send_message(chat_id=chat_id, text=text,  # type: ignore
                                                    disable_web_page_preview=True, **kwargs)

    # async def send(self, chat_type: ChatType, text: str, parse_mode=ParseMode.MARKDOWN, **kwargs):
    #     for chat_id in self.chat_ids[chat_type]:
    #         await self.app.updater.bot.send_message(chat_id=chat_id, text=text,  # type: ignore
    #                                                 parse_mode=parse_mode, **kwargs)

    async def send_photo(self, chat_type: ChatType, caption: str, photo_url: str, **kwargs):
        for chat_id in self.chat_ids[chat_type]:
            await self.app.updater.bot.send_photo(chat_id=chat_id, caption=caption,  # type: ignore
                                                  parse_mode=ParseMode.MARKDOWN,
                                                  photo=photo_url,
                                                  show_caption_above_media=True, **kwargs)

    # async def cmd_wealth(self, update: tg.Update, context: CallbackContext) -> None:
    #     try:
    #         wallet = self.services.to_address(context.args[0])
    #         log.log(f"wallet: {wallet}")

    #         wealth = self.services.get_wealth(wallet)
    #         for msg in wealth.to_msg_chunks(TG_MSG_LIMIT - 10):
    #             await update.message.reply_text(f"{msg}")

    #     except Exception as e:
    #         log.log(f"Failed: {wallet}\n{e}")
    #         await update.message.reply_text("Command failed")

    async def start(self):
        await self.app.initialize()  # inits bot, update, persistence
        await self.app.start()
        print("start polling")
        await self.app.updater.start_polling()  # type: ignore

    async def stop(self):
        await self.app.updater.stop()  # type: ignore
        await self.app.stop()
        await self.app.shutdown()

    def run(self):
        self.app.run_polling()


class TgChannel:
    def __init__(self) -> None:
        self.bot = None
        self.chat_id = 0

    async def init(self, tg_token: str, chat_id: int, description: str) -> None:
        self.bot = None
        self.chat_id = 0
        bot = None
        try:
            bot = tg.Bot(token=tg_token)
            await bot.send_message(chat_id=chat_id, text=" ")
        except tg.error.TelegramError as e:
            # This is the expected error --> OK
            if e.message == "Message must be non-empty":
                self.chat_id = chat_id
                self.bot = bot
                return
            log.log(f"Failed to initialize tg {description}({chat_id}): {e}. INACTIVE")
        except Exception as e:
            log.log(f"Failed to initialize tg {description}({chat_id}): {e}. INACTIVE")

    async def send_text(self, md_msg: str):
        if self.bot is not None:
            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    parse_mode=tg.constants.ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                    text=md_msg,
                )
            except Exception as e:
                log.log(f"Failed to send msg to tg({self.chat_id}): {e}")

    async def send_with_img(self, md_msg: str):
        if self.bot is not None:
            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    parse_mode=tg.constants.ParseMode.MARKDOWN,
                    text=md_msg,
                )
            except Exception as e:
                log.log(f"Failed to send msg to tg({self.chat_id}): {e}")


class DscrdChannel:
    def __init__(self, id: int) -> None:
        self.id = id
        self.chan = None

    def set_channel(self, client):
        try:
            self.chan = client.get_channel(self.id)
            log.log(f"Channel OK: {self.chan}")
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
                log.log(f"Failed to send embed to discord {self.chan}: {e}")
                return False
            return True
        return False

    async def send_and_log(self, message):
        if await self.send(log.slog_parent(message)):
            log.log_parent(message)
