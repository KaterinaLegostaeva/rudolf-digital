# -*- coding: UTF-8 -*-
from aiogram.fsm import StatesGroup, State


class Registration(StatesGroup):
    vk_id = State()


class Tracking(StatesGroup):
    set_track_number = State()
