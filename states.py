from aiogram.fsm.state import StatesGroup, State

class Wrap(StatesGroup):
    promo = State()
    limit = State()
    country = State()
    keys = State()
    list_keys = State()