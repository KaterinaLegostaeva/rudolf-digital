# -*- coding: UTF-8 -*-

"""
Модуль для создания и управления клавиатурами и кнопками бота.

Содержит:
- Класс Buttons: перечисление текстов и эмодзи для кнопок.
- Объекты KeyboardButton для каждой кнопки.
- Объекты ReplyKeyboardMarkup для главного меню и меню "Назад".
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import dataclasses


@dataclasses.dataclass
class Buttons:
    """Класс для хранения текстов и эмодзи кнопок бота.

    Attributes:
        REGISTRY (str): Текст кнопки "Регистрация".
        GET_MESSAGE (str): Текст кнопки "Мое задание".
        GET_HELP (str): Текст кнопки "Помощь".
        GET_TRACKER (str): Текст кнопки "Как там моя посылка?".
        SET_TRACKER (str): Текст кнопки "Заявить трекер".
        BACK (str): Текст кнопки "Вернуться в главное меню".
    """
    
    REGISTRY = '👋 Регистрация'
    GET_MESSAGE = '📨 Мое задание'
    GET_HELP = '🆘 Помощь'
    GET_TRACKER = '🎫 Как там моя посылка?'
    SET_TRACKER = '📦 Заявить трекер'
    BACK = '⏮️ Вернуться в главное меню'


btn_registry = KeyboardButton(Buttons.REGISTRY)
btn_get_message = KeyboardButton(Buttons.GET_MESSAGE)
btn_get_help = KeyboardButton(Buttons.GET_HELP)
btn_get_tracker = KeyboardButton(Buttons.GET_TRACKER)
btn_set_tracker = KeyboardButton(Buttons.SET_TRACKER)
btn_back = KeyboardButton(Buttons.BACK)


main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(btn_registry,
              btn_get_message,
              btn_get_help,
              btn_get_tracker,
              btn_set_tracker)

back_menu = ReplyKeyboardMarkup(resize_keyboard=True)
back_menu.add(btn_back)
