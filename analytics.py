import math

import discord
import plotly
import plotly.graph_objs as go

DEFAULT_NO_MSG = (None, 0.0)


def easy_div(left: int, right: int) -> float:
	right = float(right)

	if right == 0.0:
		value = 0.0
	else:
		value = left / right

	return value


class Day:
	def __init__(self, date: str):
		self.date: str = date
		self.length_sum: int = 0
		self.message_count: int = 0

	def new_message(self, length: int):
		self.length_sum += length
		self.message_count += 1


# def get_len_average(self) -> float:
# 	return easy_div(self.length_sum, self.message_count)


class Member:
	def __init__(self, name: str):
		self.name: str = name
		self.days: list = []

	def on_day(self, date: str) -> Day:
		day = None

		if len(self.days) != 0:
			tmp = self.days[-1]
			if tmp.date == date:
				day = tmp

		if not day:
			day = Day(date)
			self.days.append(day)

		return day

	def new_message(self, date: str, length: int):
		if length != 0:
			self.on_day(date).new_message(length)

	def get_count(self) -> int:
		count: int = 0

		for x in self.days:
			count += x.message_count

		return count

	def get_lengths(self) -> int:
		lengths: int = 0

		for x in self.days:
			lengths += x.length_sum

		return lengths

	def get_len_average(self) -> float:
		return easy_div(self.get_lengths(), self.get_count())


class Paranoia:
	def __init__(self):
		self.users: dict = {}
		self.dates: list = []

	def new_message(self, msg: discord.Message):
		user: discord.Member = msg.author
		wrapper: Member = self.users.setdefault(user.id, Member(user.name))
		date = msg.timestamp.date().isoformat()

		wrapper.new_message(date, len(msg.content))

		if date not in self.dates:
			self.dates.append(date)

	def normalize(self):
		data: dict = {}
		users: dict = {}

		for date in self.dates:
			data[date] = {}

		for uid in self.users:
			user = self.users[uid]
			users[uid] = user.name

			for day in user.days:
				log = 6 + math.pow(day.message_count, 0.38) * 3  # "naturalize" the number
				data[day.date][uid] = (day.message_count, log)

			print(f"&&& {user.name}: len<{user.get_count()}>, avg<{user.get_len_average():.3f}>")

		return {
			"order": list(reversed(self.dates)),
			"users": users,
			"data": data
		}


async def get_data(client: discord.Client, channel: discord.Channel, max_msg: int):
	para: Paranoia = Paranoia()
	last: discord.Message = None
	nums: int = 0
	prc: int = 0

	while True:
		listed = client.logs_from(channel, limit=100, before=last)
		last_log = last

		async for x in listed:
			para.new_message(x)
			last_log = x
			prc += 1

		if prc >= 0x500:
			nums += prc
			prc = 0
			print(f"{nums} processed")

		if last is None:
			if last_log is None:
				break
		elif last.id == last_log.id:
			break
		elif max_msg != -1 and nums >= max_msg:
			break

		last = last_log

	return para.normalize()


async def line_scan(client: discord.Client, channel: discord.Channel, max_msg: int):
	data: dict = await get_data(client, channel, max_msg)
	users: dict = {}
	plot: list = []

	for uid in data["users"]:
		users[uid] = []  # setup the Ys

	for date in data["order"]:
		entry = data["data"][date]

		for uid in users:
			log: tuple = entry.setdefault(uid, DEFAULT_NO_MSG)
			users[uid].append(log[0])  # message count

	for uid in sorted(data["users"].keys()):
		plot.append(go.Scatter(
			x=data["order"],
			y=users[uid],
			name=data["users"][uid],
			connectgaps=False
		))

	plotly.offline.plot({
		"data": plot,
		"layout": go.Layout(title=channel.name)
	}, auto_open=True)


async def scatter_scan(client: discord.Client, channel: discord.Channel, max_msg: int):
	data: dict = await get_data(client, channel, max_msg)
	users: dict = {}
	sizes: dict = {}
	plot: list = []

	for uid in data["users"]:
		users[uid] = []  # setup the Ys
		sizes[uid] = []

	for date in data["order"]:
		entry = data["data"][date]

		for uid in users:
			log: tuple = entry.setdefault(uid, DEFAULT_NO_MSG)
			users[uid].append(log[0])  # message count
			sizes[uid].append(log[1])  # lengths

	for uid in sorted(data["users"].keys()):
		plot.append(go.Scatter(
			x=data["order"],
			y=users[uid],
			mode="markers",
			name=data["users"][uid],
			marker={
				"size": sizes[uid]
			}
		))

	plotly.offline.plot({
		"data": plot,
		"layout": go.Layout(title=channel.name)
	}, auto_open=True)
