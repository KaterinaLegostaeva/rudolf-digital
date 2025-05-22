# -*- coding: UTF-8 -*-

"""Телеграм-бот для управления регистрацией пользователей и отслеживанием данных.

Основные компоненты:
    - Обработчики сообщений для команд /start, кнопок меню и состояний FSM
    - Конечные автоматы (FSM): 
        • Registration: процесс регистрации через VK ID
        • Tracking: установка трек-номера
    - Интеграция с БД SQLite через класс Database
    - Система логирования в файл и консоль
"""

import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import config
from states import Registration, Tracking
import markups as nav
from markups import Buttons as Bt
from db import Database


load_dotenv('./.env')
token = os.getenv('TOKEN')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_out = logging.StreamHandler()
file_log = logging.FileHandler("./logs/bot-info.log")
file_log.setFormatter(formatter)
console_out.setFormatter(formatter)
logging.basicConfig(handlers=(file_log, console_out), level=logging.INFO)

bot = Bot(token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database('./data/database.db')


@dp.message_handler(commands=['start'])
async def get_started(msg: types.Message):
    """Обработчик команды /start.

    Проверяет наличие пользователя в базе данных:
    - Если пользователь новый — добавляет его и отправляет стартовое сообщение.
    - Если пользователь уже существует — отправляет соответствующее сообщение.

    Args:
        msg (types.Message): Объект сообщения от пользователя.
    """
    if not db.user_exists(msg.from_user.id):
        db.add_user(msg.from_user.id)
        logging.info(config.new_user % msg.from_user.id)
        await bot.send_message(msg.from_user.id, config.start_message, reply_markup=nav.main_menu)
    else:
        await bot.send_message(msg.from_user.id, config.usr_exists_message, reply_markup=nav.main_menu)


@dp.message_handler(lambda message: message.text == Bt.REGISTRY)
async def registration(msg: types.Message):
    """ Обработчик кнопки регистрации.

    Переводит пользователя в состояние регистрации (ввод VK ID),
    отправляет сообщение с инструкцией и клавиатуру "Назад".

    Args:
        msg (types.Message): Объект сообщения от пользователя.
    """
    await bot.send_message(msg.from_user.id, config.registration_message, reply_markup=nav.back_menu)
    await Registration.vk_id.set()


@dp.message_handler(state=Registration.vk_id)
async def vk_id_processing(msg: types.Message, state: FSMContext):
    """
    Обработчик ввода VK ID в состоянии регистрации.

    Проверяет корректность введённого VK ID:
    - Если введён корректный VK ID — завершает регистрацию.
    - Если введено "Назад" — возвращает в главное меню.
    - Если введён некорректный VK ID — просит повторить ввод.

    Args:
        msg (types.Message): Объект сообщения от пользователя.
        state (FSMContext): Состояние конечного автомата (FSM).
    """
    if msg.text != Bt.BACK:
        if db.get_signup(msg.from_user.id) == 'setvkid':
            if config.is_allowed(msg.text):
                db.set_vk_id(msg.from_user.id, msg.text)
                db.set_signup(msg.from_user.id, 'complete')
                logging.info(config.new_vk_id % (msg.from_user.id, msg.text))
                await bot.send_message(msg.from_user.id, config.registration_success, reply_markup=nav.main_menu)
                await state.finish()
            else:
                await bot.send_message(msg.from_user.id, config.registration_failed)
                await Registration.vk_id.set()
        else:
            await bot.send_message(msg.from_user.id, config.registration_already, reply_markup=nav.main_menu)
            await state.finish()
    else:
        await bot.send_message(msg.from_user.id, config.back_to_menu_message, reply_markup=nav.main_menu)
        await state.finish()


@dp.message_handler(lambda message: message.text == Bt.SET_TRACKER)
async def set_track_number(msg: types.Message):
    """
    Обработчик кнопки установки трек-номера.

    Переводит пользователя в состояние ввода трек-номера,
    отправляет сообщение с инструкцией и клавиатуру "Назад".

    Args:
        msg (types.Message): Объект сообщения от пользователя.
    """
    await bot.send_message(msg.from_user.id, config.track_message, reply_markup=nav.back_menu)
    await Tracking.set_track_number.set()


@dp.message_handler(state=Tracking.set_track_number)
async def track_number_processing(msg: types.Message, state: FSMContext):
    """
    Обработчик ввода трек-номера в состоянии отслеживания.

    Проверяет корректность введённого трек-номера:
    - Если введён корректный трек-номер — сохраняет его.
    - Если введено "Назад" — возвращает в главное меню.
    - Если введён некорректный трек-номер — просит повторить ввод.

    Args:
        msg (types.Message): Объект сообщения от пользователя.
        state (FSMContext): Состояние конечного автомата (FSM).
    """
    if msg.text != Bt.BACK:
        if db.get_signup(msg.from_user.id) != 'setvkid':
            if db.get_track_number(msg.from_user.id) == 'notimplemented':
                if config.track_is_true(msg.text):
                    db.set_track_number(msg.from_user.id, msg.text)
                    logging.info(config.new_tracker % (msg.from_user.id, msg.text))
                    await bot.send_message(msg.from_user.id, config.track_success_updated, reply_markup=nav.main_menu)
                    await state.finish()
                else:
                    await bot.send_message(msg.from_user.id, config.track_failed)
                    await Tracking.set_track_number.set()
            else:
                await bot.send_message(msg.from_user.id, config.track_already, reply_markup=nav.main_menu)
                await state.finish()
        else:
            await bot.send_message(msg.from_user.id, config.registration_empty, reply_markup=nav.main_menu)
            await state.finish()
    else:
        await bot.send_message(msg.from_user.id, config.back_to_menu_message, reply_markup=nav.main_menu)
        await state.finish()


@dp.message_handler(lambda message: message.text == Bt.GET_HELP)
async def get_help(msg: types.Message):
    """Обработчик кнопки получения помощи.

    Отправляет пользователю сообщение с инструкцией или справкой.

    Args:
        msg (types.Message): Объект сообщения от пользователя.
    """
    if msg.chat.type == 'private':
        await bot.send_message(msg.from_user.id, config.help_message)


@dp.message_handler(lambda message: message.text == Bt.GET_TRACKER)
async def get_tracker(msg: types.Message):
    """Обработчик кнопки получения трек-номера.

    Проверяет статус пользователя и наличие трек-номера:
    - Если пользователь зарегистрирован и трек-номер есть — отправляет его.
    - Если пользователь не зарегистрирован или трек-номер отсутствует — сообщает об этом.

    Args:
        msg (types.Message): Объект сообщения от пользователя.
    """
    if msg.chat.type == 'private':
        if db.get_signup(msg.from_user.id) != 'setvkid':
            vk = db.get_vk_id(msg.from_user.id)
            if db.is_in_google_form(vk):
                sender_id = db.get_vk_sender_key(vk)
                owner_tg_id = db.get_user_id_via_vk(sender_id)
                track_num = db.get_track_number(owner_tg_id)
                if track_num == 'notimplemented' or owner_tg_id == '' or track_num == '':
                    await bot.send_message(msg.from_user.id,
                                           config.track_empty,
                                           reply_markup=nav.main_menu)
                else:
                    await bot.send_message(msg.from_user.id,
                                           config.got_track.format(track_num=track_num),
                                           reply_markup=nav.main_menu)
            else:
                await bot.send_message(msg.from_user.id, config.not_in_google_form, reply_markup=nav.main_menu)
        else:
            await bot.send_message(msg.from_user.id, config.registration_empty, reply_markup=nav.main_menu)


@dp.message_handler(lambda message: message.text == Bt.GET_MESSAGE)
async def get_message(msg: types.Message):
    """Обработчик кнопки получения сообщения.

    Проверяет статус пользователя и наличие данных:
    - Если пользователь зарегистрирован и данные есть — отправляет сообщение.
    - Если пользователь не зарегистрирован или данных нет — сообщает об этом.

    Args:
        msg (types.Message): Объект сообщения от пользователя.
    """
    if msg.chat.type == 'private':
        if db.get_signup(msg.from_user.id) != 'setvkid':
            vk = db.get_vk_id(msg.from_user.id)
            if db.is_in_google_form(vk):
                sent_to_id = db.get_send_to_id(msg.from_user.id)
                wishes = db.get_google_form_columns(sent_to_id)
                await bot.send_message(msg.from_user.id,
                                       config.task_message.format(name=wishes[0],
                                                                  address=wishes[1],
                                                                  post_index=wishes[2],
                                                                  new_year_attr=wishes[3],
                                                                  new_year_doings=wishes[4],
                                                                  best_gift=wishes[5],
                                                                  best_film=wishes[6],
                                                                  best_song=wishes[7],
                                                                  best_dish=wishes[8],
                                                                  best_flashback=wishes[9],
                                                                  decorations=wishes[10],
                                                                  rabbit_gift=wishes[11]),
                                       reply_markup=nav.main_menu)
            else:
                await bot.send_message(msg.from_user.id, config.not_in_google_form, reply_markup=nav.main_menu)
        else:
            await bot.send_message(msg.from_user.id, config.registration_empty, reply_markup=nav.main_menu)


@dp.message_handler()
async def default_answer(msg: types.Message):
    """Обработчик сообщений, не попавших под другие хэндлеры.

    Отправляет пользователю стандартное сообщение.

    Args:
        msg (types.Message): Объект сообщения от пользователя.
    """
    await bot.send_message(msg.from_user.id, config.default_message, reply_markup=nav.main_menu)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)