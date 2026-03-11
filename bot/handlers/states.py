"""FSM states for multistep operations."""

from aiogram.fsm.state import State, StatesGroup


class ServerStates(StatesGroup):
    adding_name = State()
    adding_api_url = State()
    renaming = State()


class KeyStates(StatesGroup):
    renaming = State()
    setting_limit = State()
