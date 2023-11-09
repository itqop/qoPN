from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import flags
from aiogram.fsm.context import FSMContext
from wrapper import create_new_key
from states import Wrap

import kb
import text
import yaml
from wrapper import init_client

router = Router()
with open('keys.yml', 'r') as file:
    data = yaml.safe_load(file)
    API_URL = data['api_url']
    CERT = data['cert_sha256']
client = init_client(api_url=API_URL, cert_sha256=CERT)


@router.message(Command("start"))
async def start_handler(msg: Message):
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


@router.callback_query(F.data == "buy_keys")
async def input_text_prompt(clbck: types.CallbackQuery, state: FSMContext):
    await state.set_state(Wrap.limit)
    await clbck.message.edit_text(text.create_key, reply_markup=kb.iexit_kb)


@router.message(Wrap.limit)
@flags.chat_action("typing")
async def generate_text(msg: Message, state: FSMContext):
    limit = msg.text
    res = await create_new_key(client=client, user_id=msg.from_user.id, limit = limit)
    if not res:
        return await msg.answer(text.err, reply_markup=kb.iexit_kb)
    await msg.answer(res, disable_web_page_preview=True)
    await menu(msg)

