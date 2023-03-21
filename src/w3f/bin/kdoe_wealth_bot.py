#!/usr/bin/env python3

import discord, pathlib
from w3f.lib import bots
from w3f.lib import whoami
import w3f.hidden_details as hd


######## Details required from the user
DISCORD_TOKEN = hd.dscrd['wealth_token']
TG_TOKEN = hd.TG['wealth_token']
######## Details required from the user

BASENAME = pathlib.PurePath(__file__).name
services = bots.Services()
dscrd_bot = bots.WealthDscrdBot(DISCORD_TOKEN, services)
tgBot = bots.TgBot(TG_TOKEN, services)

@dscrd_bot.event
async def on_ready():
    await dscrd_bot.event_on_ready()
    await dscrd_bot.chans.ipdoe_dbg.send(f"Start: {BASENAME} {whoami.get_whoami()}")

@dscrd_bot.command(description="Get your Kudoe wealth")
async def wealth(ctx: discord.commands.context.ApplicationContext, wallet):
    await dscrd_bot.cmd_wealth(ctx, wallet)

@dscrd_bot.command(description="What's the time?")
async def what_time(ctx: discord.commands.context.ApplicationContext):
    await dscrd_bot.cmd_what_time(ctx)

def main():
    whoami.log_whoami(BASENAME)
    dscrd_bot.loop.create_task(tgBot.start())
    dscrd_bot.run()

if __name__ == "__main__":
    main()
