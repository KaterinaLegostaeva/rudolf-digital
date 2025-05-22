# -*- coding: UTF-8 -*-

"""
Модуль для работы с базой данных SQLite.

Содержит классы для управления пользователями, их данными и интеграцией с Google-формой.
"""

import sqlite3


class Database:
    """Класс для работы с базой данных пользователей.

    Обеспечивает CRUD-операции для пользователей, VK ID, трек-номеров и интеграцию с Google-формой.

    Args:
        db_path (str): Путь к файлу базы данных SQLite.
    """

    def __init__(self, db_path):
        """Инициализирует соединение с базой данных и создаёт курсор.

        Args:
            db_path (str): Путь к файлу базы данных SQLite.
        """
        self.connection = sqlite3.Connection(db_path)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        """Добавляет нового пользователя в базу данных.

        Args:
            user_id (int): Идентификатор пользователя.
        """
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)",
                                       (user_id,))

    def user_exists(self, user_id):
        """Проверяет, существует ли пользователь в базе данных.

        Args:
            user_id (int): Идентификатор пользователя.

        Returns:
            bool: True, если пользователь существует, False — если нет.
        """
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?",
                                         (user_id,)).fetchall()
            return bool(len(result))

    def set_vk_id(self, user_id, vk_id):
        """Устанавливает VK ID для пользователя.

        Args:
            user_id (int): Идентификатор пользователя.
            vk_id (str): VK ID пользователя.
        """
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `vk_id` = ? WHERE `user_id` = ?",
                                       (vk_id, user_id,))

    def get_vk_id(self, user_id):
        """Возвращает VK ID пользователя.

        Args:
            user_id (int): Идентификатор пользователя.

        Returns:
            str: VK ID пользователя или пустая строка, если не найден.
        """
        vk_id = ''
        with self.connection:
            result = self.cursor.execute("SELECT `vk_id` FROM `users` WHERE `user_id` = ?",
                                         (user_id,))
            for row in result:
                vk_id = str(row[0])
            return vk_id

    def get_signup(self, user_id):
        """Возвращает статус регистрации пользователя.

        Args:
            user_id (int): Идентификатор пользователя.

        Returns:
            str: Статус регистрации пользователя.
        """
        signup = ''
        with self.connection:
            result = self.cursor.execute("SELECT `signup` FROM `users` WHERE `user_id` = ?",
                                         (user_id,))
            for row in result:
                signup = str(row[0])
            return signup

    def set_signup(self, user_id, signup):
        """Устанавливает статус регистрации пользователя.

        Args:
            user_id (int): Идентификатор пользователя.
            signup (str): Новый статус регистрации.
        """
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `signup` = ? WHERE `user_id` = ?",
                                       (signup, user_id,))

    def set_track_number(self, user_id, tracker):
        """Устанавливает трек-номер для пользователя.

        Args:
            user_id (int): Идентификатор пользователя.
            tracker (str): Трек-номер.
        """
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `track_number` = ? WHERE `user_id` = ?",
                                       (tracker, user_id,))

    def get_track_number(self, user_id):
        """Возвращает трек-номер пользователя.

        Args:
            user_id (int): Идентификатор пользователя.
        Returns:
            str: Трек-номер или пустая строка, если не найден.
        """
        tracker = ''
        with self.connection:
            result = self.cursor.execute("SELECT `track_number` FROM `users` WHERE `user_id` = ?",
                                         (user_id,))
            for row in result:
                tracker = str(row[0])
            return tracker

    def get_send_to_id(self, user_id):
        """Возвращает идентификатор получателя для пользователя из Google-формы.

        Args:
            user_id (int): Идентификатор пользователя.

        Returns:
            str: Идентификатор получателя или пустая строка, если не найден.
        """
        receiver_id = ''
        with self.connection:
            sender_vk = self.get_vk_id(user_id)
            result = self.cursor.execute("SELECT `sent_to_id` FROM `google_form` WHERE `vk_id` = ?",
                                         (sender_vk,))
            for row in result:
                receiver_id = str(row[0])
            return receiver_id

    def get_user_id_via_vk(self, vk_id):
        """Возвращает идентификатор пользователя по VK ID.

        Args:
            vk_id (str): VK ID пользователя.

        Returns:
            str: Идентификатор пользователя или пустая строка, если не найден.
        """
        receiver_id = ''
        with self.connection:
            result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `vk_id` = ?",
                                         (vk_id,))
            for row in result:
                receiver_id = str(row[0])
            return receiver_id

    def get_vk_sender_key(self, owner_vk_id):
        """Возвращает VK ID отправителя по идентификатору получателя из Google-формы.

        Args:
            owner_vk_id (str): VK ID получателя.

        Returns:
            str: VK ID отправителя или пустая строка, если не найден.
        """
        sender = ''
        with self.connection:
            result = self.cursor.execute("SELECT `vk_id` FROM `google_form` WHERE `sent_to_id` = ?",
                                         (owner_vk_id,))
            for row in result:
                sender = str(row[0])
            return sender

    def is_in_google_form(self, vk_id):
        """Проверяет, есть ли пользователь в Google-форме.

        Args:
            vk_id (str): VK ID пользователя.

        Returns:
            bool: True, если пользователь есть в Google-форме, False — если нет.
        """
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `google_form` WHERE `vk_id` = ?",
                                         (vk_id,)).fetchall()
            return bool(len(result))

    def get_google_form_columns(self, vk_id):
        """Возвращает список данных из Google-формы для пользователя.

        Args:
            vk_id (str): VK ID пользователя.

        Returns:
            list: Список данных из Google-формы.
        """
        wish_list = []
        with self.connection:
            result = self.cursor.execute(sql_query_get_from_sheet, (vk_id, )).fetchall()
            for row in result:
                wish_list = list(row)
            return wish_list


class DBMigration:
    """Класс для миграции данных в базу данных (для локального использования).

    Args:
        db_path (str): Путь к файлу базы данных SQLite.
    """

    def __init__(self, db_path):
        """Инициализирует соединение с базой данных и создаёт курсор.

        Args:
            db_path (str): Путь к файлу базы данных SQLite.
        """
        self.connection = sqlite3.Connection(db_path)
        self.cursor = self.connection.cursor()

    def add_user(self, vk_id, send_to_id, name, address,
                 post_index, new_year_attr, new_year_doings,
                 best_gift, best_film, best_song, best_dish,
                 best_flashback, decorations, rabbit_gift):
        """Добавляет пользователя в Google-форму.
        Args:
            vk_id (str): VK ID пользователя.
            send_to_id (str): Идентификатор получателя.
            name (str): Имя пользователя.
            address (str): Адрес пользователя.
            post_index (str): Почтовый индекс.
            new_year_attr (str): Атрибуты Нового года.
            new_year_doings (str): Занятия на праздники.
            best_gift (str): Лучший подарок.
            best_film (str): Лучший фильм.
            best_song (str): Лучшая песня.
            best_dish (str): Лучшее блюдо.
            best_flashback (str): Лучшее воспоминание.
            decorations (str): Украшения.
            rabbit_gift (str): Подарок кролику.
        """
        with self.connection:
            return self.cursor.execute(sql_query_migrate, (vk_id, send_to_id, name, address, post_index,
                                                           new_year_attr, new_year_doings, best_gift, best_film,
                                                           best_song, best_dish, best_flashback, decorations,
                                                           rabbit_gift,))


sql_query_migrate = """INSERT INTO `google_form` (`vk_id`, `sent_to_id`, `name`, `address`, `post_index`, \
 `new_year_attr`, `new_year_doings`, `best_gift`, `best_film`, `best_song`, `best_dish`, `best_flashback`, \
 `decorations`, `rabbit_gift`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

sql_query_get_from_sheet = """SELECT `name`, `address`, `post_index`, \
 `new_year_attr`, `new_year_doings`, `best_gift`, `best_film`, `best_song`, `best_dish`, `best_flashback`, \
 `decorations`, `rabbit_gift` FROM `google_form` WHERE `vk_id` = ?"""
