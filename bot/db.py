# -*- coding: UTF-8 -*-
import sqlite3


class Database:
    """Database-provider class"""

    def __init__(self, db_path):
        self.connection = sqlite3.Connection(db_path)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)",
                                       (user_id,))

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?",
                                         (user_id,)).fetchall()
            return bool(len(result))

    def set_vk_id(self, user_id, vk_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `vk_id` = ? WHERE `user_id` = ?",
                                       (vk_id, user_id,))

    def get_vk_id(self, user_id):
        vk_id = ''
        with self.connection:
            result = self.cursor.execute("SELECT `vk_id` FROM `users` WHERE `user_id` = ?",
                                         (user_id,))
            for row in result:
                vk_id = str(row[0])
            return vk_id

    def get_signup(self, user_id):
        signup = ''
        with self.connection:
            result = self.cursor.execute("SELECT `signup` FROM `users` WHERE `user_id` = ?",
                                         (user_id,))
            for row in result:
                signup = str(row[0])
            return signup

    def set_signup(self, user_id, signup):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `signup` = ? WHERE `user_id` = ?",
                                       (signup, user_id,))

    def set_track_number(self, user_id, tracker):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `track_number` = ? WHERE `user_id` = ?",
                                       (tracker, user_id,))

    def get_track_number(self, user_id):
        tracker = ''
        with self.connection:
            result = self.cursor.execute("SELECT `track_number` FROM `users` WHERE `user_id` = ?",
                                         (user_id,))
            for row in result:
                tracker = str(row[0])
            return tracker

    def get_send_to_id(self, user_id):
        receiver_id = ''
        with self.connection:
            sender_vk = self.get_vk_id(user_id)
            result = self.cursor.execute("SELECT `sent_to_id` FROM `google_form` WHERE `vk_id` = ?",
                                         (sender_vk,))
            for row in result:
                receiver_id = str(row[0])
            return receiver_id

    def get_user_id_via_vk(self, vk_id):
        receiver_id = ''
        with self.connection:
            result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `vk_id` = ?",
                                         (vk_id,))
            for row in result:
                receiver_id = str(row[0])
            return receiver_id

    def get_vk_sender_key(self, owner_vk_id):
        sender = ''
        with self.connection:
            result = self.cursor.execute("SELECT `vk_id` FROM `google_form` WHERE `sent_to_id` = ?",
                                         (owner_vk_id,))
            for row in result:
                sender = str(row[0])
            return sender

    def is_in_google_form(self, vk_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `google_form` WHERE `vk_id` = ?",
                                         (vk_id,)).fetchall()
            return bool(len(result))

    def get_google_form_columns(self, vk_id):
        wish_list = []
        with self.connection:
            result = self.cursor.execute(sql_query_get_from_sheet, (vk_id, )).fetchall()
            for row in result:
                wish_list = list(row)
            return wish_list


class DBMigration:
    # FOR LOCAL USE ONLY
    # read-only object
    def __init__(self, db_path):
        self.connection = sqlite3.Connection(db_path)
        self.cursor = self.connection.cursor()

    def add_user(self, vk_id, send_to_id, name, address,
                 post_index, new_year_attr, new_year_doings,
                 best_gift, best_film, best_song, best_dish,
                 best_flashback, decorations, rabbit_gift):
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
