from aiogram.fsm.state import StatesGroup, State

class Wrap(StatesGroup):
    promo = State()
    limit = State()