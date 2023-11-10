from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram import flags
from aiogram.fsm.context import FSMContext
from wrapper import create_new_key
from states import Wrap
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asyncio import sleep

import kb
import text
import yaml
from wrapper import init_client, real_used, delete_key
from db import Database


router = Router()

with open('keys.yml', 'r') as file:
    data = yaml.safe_load(file)
    API_URL = data['api_url']
    CERT = data['cert_sha256']
    DB_URL = data['db_url']
    DB_PORT = data['db_port']
    DB_NAME = data['db_name']
    DB_USER = data['db_user']
    DB_PASSWORD = data['db_password']
    PASSWORD = data['tg_pass']

db = Database(DB_URL, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
clients = init_client(api_url=API_URL, cert_sha256=CERT)
country_emojis = {
    "DE": "🇩🇪",
    "NL": "🇳🇱",
    "NO": "🇳🇴",
    "TR": "🇹🇷",
    "RU": "🇷🇺"
}
class ListKeys(CallbackData, prefix="keys"):
    action: str
    name: str


async def update_data_periodically():
    while True:
        try:
            real_use = await real_used(clients['DE'])
            await db.update_used(real_use)
        except Exception as e:
            print(f"Error updating data: {e}")
        await sleep(6400)
        

@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await state.clear()
    user_id = str(msg.from_user.id)
    user_name = msg.from_user.username
    user_exists = await db.get_balance(user_id)

    if not user_exists and user_exists != 0:
        if not user_name: user_name = "null"
        await db.add_user(user_id, user_name)
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@router.callback_query(F.data == "menu")
async def clear_states(clbck: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await clbck.message.edit_text(text.menu, reply_markup=kb.menu)


@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu)


@router.callback_query(F.data == "help")
async def help_data(clbck: types.CallbackQuery, state: FSMContext):
    await clbck.message.edit_text(text.help, reply_markup=kb.iexit_kb)


@router.callback_query(F.data == "balance")
async def balance_data(clbck: types.CallbackQuery, state: FSMContext):
    rub = await db.get_balance(str(clbck.from_user.id))
    await clbck.message.edit_text(text.balance.format(rub=str(rub)), reply_markup=kb.iexit_kb)


@router.callback_query(F.data == "list_keys")
async def list_keys_data(clbck: types.CallbackQuery, state: FSMContext):
    await state.set_state(Wrap.list_keys)
    keys = await db.get_access_keys(str(clbck.from_user.id))
    keyboard = []
    states = {}
    for row in keys:
        country = row['country']
        name = row['name']
        used = row['used']
        limits = row['limits']
        keys_url = row['keys']

        country_emoji = country_emojis.get(country, "")

        button_text = f"{country_emoji} | {name} | {used}/{limits}"
        states[name] = f"{country_emoji}|{keys_url}|{used}/{limits}"
        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=ListKeys(
            action="get_key", name=name
            ).pack())])
    
    #chunk_size = 2
    #keyboard = [keyboard[i:i + chunk_size] for i in range(0, len(keyboard), chunk_size)]
    await state.update_data(list_keys=states)
    keyboard.append([InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await clbck.message.edit_text(text.list_keys, reply_markup=keyboard)

@router.callback_query(ListKeys.filter(F.action == "get_key"))
async def get_data_key(clbck: types.CallbackQuery, state: FSMContext,  callback_data: ListKeys):
    ids = callback_data.name
    list_keys = (await state.get_data())['list_keys'][ids]
    emj, key, used = list_keys.split("|")
    text = f"Страна - {emj}\nВаш ключ с id {ids} - \n{key}\n\nИспользовано: {used}"
    list_keys_actions = [
    [InlineKeyboardButton(text="Повысить лимит", callback_data=ListKeys(
            action="update_key", name=ids).pack())],
    [InlineKeyboardButton(text="Удалить ключ", callback_data=ListKeys(
            action="delete_key", name=ids).pack())],
    [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
    ]
    list_keys_actions = InlineKeyboardMarkup(inline_keyboard=list_keys_actions)
    await clbck.message.edit_text(text, reply_markup=list_keys_actions)

@router.callback_query(ListKeys.filter(F.action == "update_key"))
async def delete_key_handler(clbck: types.CallbackQuery, state: FSMContext, callback_data: ListKeys):
     await clbck.message.edit_text("В разработке", reply_markup=kb.iexit_kb)

@router.callback_query(ListKeys.filter(F.action == "delete_key"))
async def delete_key_handler(clbck: types.CallbackQuery, state: FSMContext, callback_data: ListKeys):
    ids = callback_data.name
    list_keys = (await state.get_data())['list_keys'][ids]
    emj, key, used = list_keys.split("|")
    await db.delete_access_key(keys=key)
    await delete_key(clients["DE"], key)
    
    await clbck.message.edit_text(text.delete, reply_markup=kb.iexit_kb)

@router.callback_query(F.data == "free_tokens")
async def free_tokens(clbck: types.CallbackQuery, state: FSMContext):
    await clbck.message.edit_text(text.free, reply_markup=kb.iexit_kb)


@router.callback_query(F.data == "buy_tokens")
async def buy_tokens(clbck: types.CallbackQuery, state: FSMContext):
    await clbck.message.edit_text(text.buy, reply_markup=kb.iexit_kb)

@router.callback_query(F.data == "promo")
async def promo_choose(clbck: types.CallbackQuery, state: FSMContext):
    await state.set_state(Wrap.promo)
    await clbck.message.edit_text(text.promo, reply_markup=kb.iexit_kb)

@router.message(Wrap.promo)
@flags.chat_action("typing")
async def promo_enter(msg: Message, state: FSMContext):
    promo = msg.text
    tokens = await db.get_promo_code(code=promo)
    if tokens:
        if not tokens["used"]:
            await msg.answer(text=text.promo_accept.format(rub=str(tokens["tokens"])), reply_markup=kb.iexit_kb)
            await db.update_balance(user_id=str(msg.from_user.id), number=int(tokens["tokens"]))
            await db.mark_promo_code_as_used(code=str(promo))
        else:
            await msg.answer(text=text.promo_used, reply_markup=kb.iexit_kb)
    else: 
        await msg.answer(text=text.promo_error, reply_markup=kb.iexit_kb)


@router.callback_query(F.data == "buy_keys")
async def buy_keys_data(clbck: types.CallbackQuery, state: FSMContext):
    await state.set_state(Wrap.limit)
    await clbck.message.edit_text(text.create_key, reply_markup=kb.iexit_kb)

@router.message(Wrap.limit)
@flags.chat_action("typing")
async def typ_limit(msg: Message, state: FSMContext):
    limit = msg.text
    if int(limit) < 1:
        return await msg.answer(text.err, reply_markup=kb.iexit_kb)
    counts = await db.count_rows_by_user_id(str(msg.from_user.id))
    if counts >=5:
        return await msg.answer(text.err_count, reply_markup=kb.iexit_kb)
    await msg.answer(text=text.list_places, reply_markup=kb.countries)
    await state.update_data(limit=limit)


@router.callback_query(F.data == "buy_germany")
async def buy_germany_vpn(clbck: types.CallbackQuery, state: FSMContext):
    limit =(await state.get_data())["limit"]
    balance = await db.get_balance(str(clbck.from_user.id))
    if balance < int(limit):
        return await clbck.message.answer(text=text.low_balance, reply_markup=kb.iexit_kb)
    
    id = "DE"
    res = create_new_key(client=clients[id], user_id=str(clbck.from_user.id), limit = int(limit))
    if not res:
        return await clbck.message.edit_text(text.err, reply_markup=kb.iexit_kb)
    await db.add_access_key(user_id=str(clbck.from_user.id), keys=res[0].access_url, limits=int(limit), country=id, name_id=res[1])
    await db.update_balance(user_id=str(clbck.from_user.id), number=-1 * int(limit))
    await clbck.message.edit_text(f"Ваш ключ:\n{res[0].access_url}", disable_web_page_preview=True)
    await clbck.message.answer(text.text_invite, disable_web_page_preview=True)
    await menu(clbck.message)


@router.message(Command("add_promo"))
async def add_promo_handler(message: types.Message, state: FSMContext):
    command_parts = message.text.split()
    if len(command_parts) == 4:
        _, password, promo_code, num_tokens = command_parts
        if password == PASSWORD:
            await db.add_promo_code(promo_code, int(num_tokens))
            await message.answer(f"Промокод {promo_code} успешно добавлен в базу данных.")
        else:
            await message.answer("Неверный пароль.")
    else:
        await message.answer("Неверное количество аргументов. Используйте /add_promo password promo_code num_tokens.")