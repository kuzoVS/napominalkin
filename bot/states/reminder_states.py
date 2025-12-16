from aiogram.fsm.state import State, StatesGroup


class CreateReminderStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_date = State()
    waiting_for_time = State()


class RemindOtherStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_text = State()
    waiting_for_date = State()
    waiting_for_time = State()


class DailyReminderStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_time = State()
