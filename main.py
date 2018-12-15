import asyncio

import discord

import analytics

# CONFIGS
MAX_MESSAGES: int = -1  # set to -1 to use all messages, otherwise the number given
IS_A_BOT: bool = False  # set to True if it's for a bot
TOKEN: str = "TOKEN GOES HERE"  # token being used

# EDIT PAST HERE AT YOUR OWN RISK
me_irl: discord.Client = discord.Client()


@me_irl.event
@asyncio.coroutine
def on_ready():
	print(f"Started up for {me_irl.user.name}")


@me_irl.event
@asyncio.coroutine
def on_message(msg: discord.Message):
	if IS_A_BOT or msg.author.id == me_irl.user.id:
		if msg.content == ".line":  # shows amount of messages over weeks
			yield from analytics.line_scan(me_irl, msg.channel, MAX_MESSAGES)
		elif msg.content == ".scatter":  # shows daily messages and length average
			yield from analytics.scatter_scan(me_irl, msg.channel, MAX_MESSAGES)


if TOKEN == "TOKEN GOES HERE":
	TOKEN = input("Please enter a token or set the `TOKEN` variable in the main script\n")

me_irl.run(TOKEN, bot=IS_A_BOT)
me_irl.close()
