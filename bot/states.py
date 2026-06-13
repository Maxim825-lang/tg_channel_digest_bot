from aiogram.fsm.state import State, StatesGroup


class Dialog(StatesGroup):
    waiting = State()
