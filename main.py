from vkbottle.bot import Bot, Message, MessageEvent
from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback, GroupTypes, GroupEventType
from vkbottle import API, CtxStorage, PhotoMessageUploader, BaseStateGroup, DocMessagesUploader
from vkbottle.modules import json
import asyncio
import time
import sqlite3
import re


db = sqlite3.connect('server.db')
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users (
	nickname TEXT,
	vk_id TEXT,
	group_user INT
	)""")

user_groups = """
	USER GROUPS:
		1 - ГУ МВД-П
		2 - ГУ МВД-М
		3 - ГУ МВД-Н
		4 - Адвокат
		5 - Лидер ГУ МВД-П
		6 - Лидер ГУ МВД-М
		7 - Лидер ГУ МВД-Н
		8 - Лидер ЧО
"""


user_groups_list = ['ГУ МВД-П', 'ГУ МВД-М', 'ГУ МВД-Н', 'Адвокат', 'Лидер ГУ МВД-П', 'Лидер ГУ МВД-М', 'Лидер ГУ МВД-Н', 'Лидер ЧО']

sql.execute("""CREATE TABLE IF NOT EXISTS orders (
	numbers INT,
	nickname TEXT,
	vk_id TEXT,
	reasons TEXT,
	jailtime INT,
	where_from TEXT,
	screen TEXT
	)""")


db.commit()

bot = Bot("vk1.a.u2g2xziFM_wi4hS3AMdtQgk1E2-9m52xaV2Cw5xVmBMUsJ3sWDD6vTOFwySnjokH0obnZgLQp1WWn1yzfnEHSuwO8356w1p6RpEXx0pJvWR_dEwopRh2LreJ7wUYiRgWcnKe50zjbtmUs-93YBe5OMUhpcg19h8jPHLgL28kmoKoHFTtcHR-a7YD9Du2zynBC1C2CrZTR339SUGkw2Kc6w")
photo_uploader = PhotoMessageUploader(bot.api)
doc_uploader = DocMessagesUploader(bot.api)
print('[+] VK Сonnected')

def findWholeWord(w):
    return re.compile('{0}'.format(w), flags=re.IGNORECASE).search

def get_from_where(text):
	if findWholeWord('прив')(text.lower()) != None:
		return 1
	elif findWholeWord('мир')(text.lower()) != None:
		return 2
	elif findWholeWord('нев')(text.lower()) != None:
		return 3
	else:
		return 4

async def get_data_from_link(api: API, link: str) -> bytes:
	return bytes(await api.http_client.request_content(link, "GET"))

ctx = CtxStorage()
class RegData(BaseStateGroup):
	NICKNAME = 0
	REASON = 1
	JAILTIME = 2
	SCREENSHOT = 3
	WHERE_FROM = 4

@bot.on.message(text="/id")
async def id_peer(message: Message):
	await message.answer(message.peer_id)

@bot.on.message(text="/bd12931273129512346")
async def get_bd(message: Message):
	for user in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE vk_id = '{message.from_id}'"):
		if user[2] == 8:
		    doc = await doc_uploader.upload(title='server.db', file_source=r"server.db", peer_id=message.peer_id)
		    await message.answer(attachment=doc)
		else:
			await message.answer('Недостаточно прав❗')

@bot.on.message(text=["/гувд", "/guvd"])
async def get_guvd(message: Message):
	text = '[ГУ МВД-П]'
	for user in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '5'"):
		text += f'\n@id{user[0]} ({user[1]}) -> [{user_groups_list[int(user[2])-1]}]'
	for user in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '1'"):
		text += f'\n@id{user[0]} ({user[1]}) -> [{user_groups_list[int(user[2])-1]}]'
	text += '\n\n[ГУ МВД-М]'
	for user in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '6'"):
		text += f'\n@id{user[0]} ({user[1]}) -> [{user_groups_list[int(user[2])-1]}]'
	for user in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '2'"):
		text += f'\n@id{user[0]} ({user[1]}) -> [{user_groups_list[int(user[2])-1]}]'
	text += '\n\n[ГУ МВД-Н]'
	for user in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '7'"):
		text += f'\n@id{user[0]} ({user[1]}) -> [{user_groups_list[int(user[2])-1]}]'
	for user in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '3'"):
		text += f'\n@id{user[0]} ({user[1]}) -> [{user_groups_list[int(user[2])-1]}]'
	await message.answer(text)

@bot.on.message(text=["/адвокаты", "/lawyers"])
async def get_guvd(message: Message):
	text = '[Адвокаты]'
	for user in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '8'"):
		text += f'\n@id{user[0]} ({user[1]}) -> [{user_groups_list[int(user[2])-1]}]'
	for user in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '4'"):
		text += f'\n@id{user[0]} ({user[1]}) -> [{user_groups_list[int(user[2])-1]}]'
	await message.answer(text)

@bot.on.private_message(text="Начать")
async def start_message(message: Message):
	keyboard = (Keyboard(one_time=False, inline=False).add(Text("Сделать заказ"), color=KeyboardButtonColor.POSITIVE)).get_json()
	await message.answer("Нажмите на кпоку дабы сделать заказ", keyboard=keyboard)


@bot.on.private_message(lev="Сделать заказ")
async def start_order(message: Message):
	await bot.state_dispenser.set(message.peer_id, RegData.NICKNAME)
	return 'Введите ваш никнейм:'

@bot.on.private_message(state=RegData.NICKNAME)
async def get_user_order(message: Message):
	ctx.set("nickname", message.text)
	await bot.state_dispenser.set(message.peer_id, RegData.REASON)
	return 'Введите причину задержания:'

@bot.on.private_message(state=RegData.REASON)
async def get_reason_order(message: Message):
	ctx.set("reason", message.text)
	await bot.state_dispenser.set(message.peer_id, RegData.JAILTIME)
	return 'Введите cрок заключения (/jailtime):'


@bot.on.private_message(state=RegData.JAILTIME)
async def get_jailtime_order(message: Message):
	ctx.set("jailtime", message.text)
	await bot.state_dispenser.set(message.peer_id, RegData.SCREENSHOT)
	return 'Доказательства заключения (скрин с /timestamp и /jailtime):'


@bot.on.private_message(state=RegData.SCREENSHOT)
async def get_screen_order(message: Message):
	if message.attachments:
		ctx.set("screen", message.attachments[0].photo.sizes[4].url)
		await bot.state_dispenser.set(message.peer_id, RegData.WHERE_FROM)
		return 'Введите в какой дежурной части вы находитесь:'
	else:
		await message.answer(f'Вы не прикрепили фото.\nЗаполните заявку заново❗')
		await bot.state_dispenser.delete(message.peer_id)

@bot.on.private_message(state=RegData.WHERE_FROM)
async def get_screen_order(message: Message):
	ctx.set("from_where", message.text)

	for i in sql.execute(f"SELECT numbers FROM orders"):
		number_order = i[0] + 1
	nickname = ctx.get('nickname')
	reason = ctx.get('reason')
	jailtime = ctx.get('jailtime')
	screen = ctx.get('screen')
	from_where = ctx.get('from_where')
	from_where_2 = get_from_where(from_where)
	text_message = f'Заказ: №{number_order}\nNickname: {nickname} 🤵\nПричина задержания: {reason} ⛓️\nСрок задержания: {jailtime} ⌚\nДежурная часть: {from_where} 🏢'

	KEYBOARD = (Keyboard(inline=True).add(Callback(f"Взять❗", payload={"peer": message.peer_id, 'text':text_message, 'type_btn':'en', 'number_order':number_order, 'guvd':from_where_2, 'nickname':nickname}), color=KeyboardButtonColor.POSITIVE).add(Callback(f"Отклонить❗", payload={"peer": message.peer_id, 'text':text_message, 'type_btn':'dis', 'number_order':number_order, 'guvd':from_where_2, 'nickname':nickname}), color=KeyboardButtonColor.NEGATIVE).get_json())
	sql.execute(f"INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)", (number_order, nickname, message.peer_id, reason, jailtime, from_where, screen))
	db.commit()
	bytePicture =  await get_data_from_link(bot.api, link=screen)
	photo = await photo_uploader.upload(bytePicture)
	await message.answer(f'Ваш nickname: {nickname} 🤵\nПричина задержания: {reason} ⛓️\nСрок задержания: {jailtime} ⌚\nДежурная часть: {from_where} 🏢\n\nДанные отправлены сотрудникам организации 🗣', attachment=photo, random_id=0)
	await bot.api.messages.send(peer_id=2000000002, message=text_message, random_id=0, keyboard=KEYBOARD, attachment=photo)
	await bot.state_dispenser.delete(message.peer_id)


def give_group(rank_from, rank_user):
	if rank_from == 5 and rank_user == 1:
		return True
	elif rank_from == 6 and rank_user == 2:
		return True
	elif rank_from == 7 and rank_user == 3:
		return True
	elif rank_from == 8:
		return True
	else:
		return False

@bot.on.message(text=["/роль <item>", '/роль'])
async def get_role(message: Message, item=None):
	if item == None:
		for i in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE vk_id = {message.from_id}"):
			await message.answer(f'Ваша роль: [{user_groups_list[int(i[2])-1]}]')
	else:
		vk_link = item.replace('https://vk.com/','').replace('https://m.vk.com/','').replace("@","")
		if vk_link[0] == "[":
			vk_link = vk_link.split("|")[1][0:-1]
		user_info = await bot.api.request('users.get', {'user_ids' : vk_link})
		if len(user_info['response']) != 0:
			for i in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE vk_id = {user_info['response'][0]['id']}"):
				await message.answer(f'У @id{i[0]} ({i[1]}) роль: [{user_groups_list[int(i[2])-1]}]')
		else:
			await message.answer(f"Пользователя с такой ссылкой нет❗")


@bot.on.message(text=["/user <item>", '/user'])
async def new_user(message: Message, item=None):
	for i in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE vk_id = {message.from_id}"):
		if i[2] >= 5:
			if item != None:
				args_command = item.split()
				if len(args_command) == 3:
					if args_command[0].split('/')[0] == 'https:' or args_command[0][0] == '[':
						if args_command[1].isdigit():
							if int(args_command[1]) <= 8:
								if give_group(i[2], int(args_command[1])):
									vk_link = args_command[0].replace('https://vk.com/','').replace('https://m.vk.com/','').replace("@","")
									if vk_link[0] == "[":
										vk_link = vk_link.split("|")[1][0:-1]
									user_info = await bot.api.request('users.get', {'user_ids' : vk_link})
									if len(user_info['response']) != 0:
										sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE vk_id = {user_info['response'][0]['id']}")
										if sql.fetchone() is None:
											sql.execute(f"INSERT INTO users VALUES (?, ?, ?)", (args_command[2], user_info['response'][0]['id'], int(args_command[1])))
											db.commit()
											await message.answer(f"Сотруднику @id{user_info['response'][0]['id']} ({args_command[2]}) была выдана роль [{user_groups_list[int(args_command[1])-1]}]❗")
										else:
											for i2 in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE vk_id = {user_info['response'][0]['id']}"):
												if int(i2[2]) <= int(i[2]):
													sql.execute(f"UPDATE users SET group_user = {int(args_command[1])} WHERE vk_id = {user_info['response'][0]['id']}")
													db.commit()
													await message.answer(f"Сотруднику @id{user_info['response'][0]['id']} ({args_command[2]}) была изменена роль [{user_groups_list[int(i2[2])-1]} -> {user_groups_list[int(args_command[1])-1]}]❗")
												else:
													await message.answer(f"Недостаточно прав❗")
									else:
										await message.answer(f"Пользователя с такой ссылкой нет❗")
								else:
									await message.answer(f"Недостаточно прав❗")
							else:
								await message.answer(f"Роли с такой цифрой нет❗\n\n" + user_groups)
						else:
							await message.answer(f"Роль должна быть цифрой❗\n\n" + user_groups)
					else:
						await message.answer(f"Первым аргументом должна быть ссылка на пользователя❗")
				else:
					await message.answer(f"Вы не написали один из аргументов команды❗")
		else:
			await message.answer(f"У вас недостаточно прав❗")


@bot.on.message(text=["/clear <item>", '/clear'])
async def delete_user(message: Message, item=None):
	for i in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE vk_id = {message.from_id}"):
		if i[2] >= 5:
			if item != None:
				if item.split('/')[0] == 'https:' or item[0] == '[':
					vk_link = item.replace('https://vk.com/','').replace('https://m.vk.com/','').replace("@","")
					if vk_link[0] == "[":
						vk_link = vk_link.split("|")[1][0:-1]
					user_info = await bot.api.request('users.get', {'user_ids' : vk_link})
					if len(user_info['response']) != 0:
						sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE vk_id = {user_info['response'][0]['id']}")
						if sql.fetchone() is None:
							await message.answer(f"Пользователь не зарегистрирован❗")
						else:
							for user in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE vk_id = {user_info['response'][0]['id']}"):
								if give_group(i[2], int(user[2])):
									sql.execute('DELETE FROM users WHERE vk_id=?', (user_info['response'][0]['id'],))
									await message.answer(f"Сотрудник @id{user[0]} ({user[1]}) был удален❗")
									db.commit()
								else:
									await message.answer(f"У вас недостаточно прав❗")
					else:			
						await message.answer(f"Пользователя с такой ссылкой нет❗")
				else:
					await message.answer(f"Аргументом к этой команде должна быть ссылка на пользователя❗")
			else:
				await message.answer(f"Вы не написали ссылку на пользователя❗")
		else:
			await message.answer(f"У вас недостаточно прав❗")



@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def message_event_handler(event: MessageEvent):
	message_id = event.object.conversation_message_id
	peer_id = event.object.peer_id
	type_btn = event.object.payload["type_btn"]
	sql.execute(f"SELECT vk_id FROM users WHERE vk_id = {event.object.user_id}")
	if sql.fetchone() is None:
		await bot.api.messages.send(peer_id=peer_id, message=f'@id{event.object.user_id} (NoName) попросите лидера организации Вас зарегистрировать в боте, дабы брать заказы от клиентов❗', random_id=0)
	else:
		for user in sql.execute(f"SELECT nickname, vk_id, group_user FROM users WHERE vk_id = '{event.object.user_id}'"):
			if type_btn == 'en':
				user_id_inlian = event.object.payload["peer"]
				user_id_accepted = event.object.user_id
				text = event.object.payload["text"]
				number_order = event.object.payload["number_order"]
				guvd = event.object.payload["guvd"]
				nickname_order = event.object.payload["nickname"]
				await bot.api.messages.send(peer_id=peer_id, message=f'@id{user_id_accepted} ({user[0]}) принял заказ №{number_order}❗', random_id=0)
				await bot.api.messages.send(peer_id=int(user_id_inlian), message=f'⚠ Ваш заказ приняли. Ожидайте сотрудника❗', random_id=0)
				KEYBOARD = (Keyboard(inline=True)
					.add(Callback(f"Отказаться от заказа❗", payload={"peer": user_id_inlian, 'text':text, 'type_btn':'dis_proc', 'user_id_accepted': user_id_accepted, 'number_order': number_order}), color=KeyboardButtonColor.NEGATIVE)
					.add(Callback(f"Заказ выполнен❗", payload={"peer": user_id_inlian, 'text':text, 'type_btn':'сompleted', 'user_id_accepted': user_id_accepted, 'number_order': number_order}), color=KeyboardButtonColor.POSITIVE).row()
					.add(Callback(f"Уведомить ГУВД❗", payload={"peer": user_id_inlian, 'text':text, 'type_btn':'allow_guvd', 'user_id_accepted': user_id_accepted, 'guvd':guvd, 'number_order': number_order, 'nickname':nickname_order})).get_json())
				text = text + f'\n\n⚠Статус заказа: Принят❗\nПринял: @id{user_id_accepted} ({user[0]})'
				await bot.api.request('messages.edit', {"peer_id": int(peer_id), "conversation_message_id": int(message_id), 'message':text, 'keyboard':KEYBOARD})
			elif type_btn == 'dis':
				user_id_inlian = event.object.payload["peer"]
				user_id_accepted = event.object.user_id
				text = event.object.payload["text"]
				number_order = event.object.payload["number_order"]
				await bot.api.messages.send(peer_id=peer_id, message=f'@id{user_id_accepted} ({user[0]}) отклонил заказ №{number_order}❗', random_id=0)
				await bot.api.messages.send(peer_id=int(user_id_inlian), message=f'⚠ К сожалению, Ваш заказ отклонили❗', random_id=0)
				text = text + f'\n\n⚠Статус заказа: Отклонен❗\nОтклонил: @id{user_id_accepted} ({user[0]})'
				await bot.api.request('messages.edit', {"peer_id": int(peer_id), "conversation_message_id": int(message_id), 'message':text})
			elif type_btn == 'dis_proc':
				user_id_inlian = event.object.payload["peer"]
				user_id_accepted = event.object.payload["user_id_accepted"]
				text = event.object.payload["text"]
				number_order = event.object.payload["number_order"]
				if event.object.user_id == user_id_accepted or user[2] == 8:
					await bot.api.messages.send(peer_id=peer_id, message=f'@id{user_id_accepted} ({user[0]}) отклонил заказ №{number_order}❗', random_id=0)
					await bot.api.messages.send(peer_id=int(user_id_inlian), message=f'⚠ К сожалению, Ваш заказ отклонили❗', random_id=0)
					text = text + f'\n\n⚠Статус заказа: Отклонен❗\nОтклонил: @id{user[1]} ({user[0]})'
					await bot.api.request('messages.edit', {"peer_id": int(peer_id), "conversation_message_id": int(message_id), 'message':text})				
				else:
					await event.show_snackbar("Вы не принимали данный заказ, по этому вы не можете его отклонить.")
			elif type_btn == 'сompleted':
				user_id_inlian = event.object.payload["peer"]
				user_id_accepted = event.object.payload["user_id_accepted"]
				text = event.object.payload["text"]
				number_order = event.object.payload["number_order"]
				if event.object.user_id == user_id_accepted or user[2] == 8:
					await bot.api.messages.send(peer_id=peer_id, message=f'@id{user[1]} ({user[0]}) успешно выполнил заказ №{number_order}❗', random_id=0)
					await bot.api.messages.send(peer_id=int(user_id_inlian), message=f'⚠ Ваш заказ выполнен, не забудьте оставить отзыв о нас❗', random_id=0)
					text = text + f'\n\n⚠Статус заказа: Выполнен❗\nВыполнил: @id{user[1]} ({user[0]})'
					await bot.api.request('messages.edit', {"peer_id": int(peer_id), "conversation_message_id": int(message_id), 'message':text})
				else:
					await event.show_snackbar("Вы не принимали данный заказ, по этому вы не можете его отклонить.")
			elif type_btn == 'allow_guvd':
				user_id_inlian = event.object.payload["peer"]
				user_id_accepted = event.object.payload["user_id_accepted"]
				text = event.object.payload["text"]
				number_order = event.object.payload["number_order"]
				guvd = event.object.payload["guvd"]
				nickname_order = event.object.payload["nickname"]
				if event.object.user_id == user_id_accepted or user[2] == 8:
					if guvd == 1:
						allow_guvd = f'Уважаемые, пришел новый заказ❗\nДежурная часть: Приволжск\n'
						for i in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '5'"):
							allow_guvd += f'@id{i[0]} ({i[1]}), '
						for i in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '1'"):
							allow_guvd += f'@id{i[0]} ({i[1]}), '
						allow_guvd += f'\nNickname клиента: @id{user_id_inlian} ({nickname_order})\nNickname адвоката: @id{user[1]} ({user[0]})'
						await bot.api.messages.send(peer_id=2000000003, message=allow_guvd, random_id=0)
					elif guvd == 2:
						allow_guvd = f'Уважаемые, пришел новый заказ❗\nДежурная часть: Мирный\n'
						for i in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '6'"):
							allow_guvd += f'@id{i[0]} ({i[1]}), '
						for i in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '2'"):
							allow_guvd += f'@id{i[0]} ({i[1]}), '
						allow_guvd += f'\nNickname клиента: @id{user_id_inlian} ({nickname_order})\nNickname адвоката: @id{user[1]} ({user[0]})'
						await bot.api.messages.send(peer_id=2000000003, message=allow_guvd, random_id=0)
					elif guvd == 3:
						allow_guvd = f'Уважаемые, пришел новый заказ❗\nДежурная часть: Невский\n'
						for i in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '7'"):
							allow_guvd += f'@id{i[0]} ({i[1]}), '
						for i in sql.execute(f"SELECT vk_id, nickname, group_user FROM users WHERE group_user = '3'"):
							allow_guvd += f'@id{i[0]} ({i[1]}), '
						allow_guvd += f'\nNickname клиента: @id{user_id_inlian} ({nickname_order})\nNickname адвоката: @id{user[1]} ({user[0]})'
						await bot.api.messages.send(peer_id=2000000003, message=allow_guvd, random_id=0)
					elif guvd == 4:
						await event.show_snackbar("ГУ МВД неопределенно, вам стоит самостоятельно их отметить!")
				else:
					await event.show_snackbar("Вы не принимали данный заказ, по этому вы не можете его отклонить.")

bot.run_forever()