from aiogram.fsm.state import State, StatesGroup


class NeiroChatStates(StatesGroup):
    waiting_for_text_prompt = State()
    waiting_for_image_prompt = State()
