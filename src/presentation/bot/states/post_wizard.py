from aiogram.fsm.state import State, StatesGroup


class PostWizard(StatesGroup):
    choosing_type = State()
    collecting_content = State()
    collecting_buttons = State()
