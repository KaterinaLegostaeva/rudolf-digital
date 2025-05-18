# -*- coding: UTF-8 -*-
import pandas as pd
from bot import config
import random
import codecs
from collections import OrderedDict
from collections import deque

from bot.db import DBMigration


class Generator:
    """Only for local use! Class allows you to generate pairs of participants and .txt file with messages"""

    def __init__(self, path='./data/data.xlsx'):
        """Constructor provides to work with a path to data table"""
        self._path = path
        self._pairs = {}
        self._vk_id = []

    # a pack of getters for protected members
    def get_pairs(self):
        return self._pairs

    def get_people(self):
        return self._vk_id

    def get_people_from_doc(self):
        """Getting people from the list in the document"""
        data = pd.read_excel('./data/data.xlsx')
        self._vk_id = tuple(data['vk_id'])
        return self._vk_id

    def compare_people(self):
        """ Given a list of people, assign each one a secret santa partner
            from the list and return the pairings as a dict. Implemented to always
            create a perfect cycle """
        self.get_people_from_doc()
        shuffle_ids = list(self._vk_id)
        random.shuffle(shuffle_ids)
        partners = deque(shuffle_ids)
        partners.rotate()
        self._pairs = OrderedDict(zip(self._vk_id, partners))
        return self._pairs

    def generate_message(self):
        """Generates messages to a text-file in the current directory"""
        print('WARNING: generate_message() is deprecated and will be removed in a future')
        data = pd.read_excel(self._path)
        with codecs.open('messages.txt', 'w', "utf_8_sig") as f:
            self.compare_people()
            for guy in self._pairs.keys():
                gifted_name = self._pairs[guy]
                row_i = data.loc[data['ФИО'] == gifted_name].index[0]
                address = data.iloc[row_i][...]
                index = data.iloc[row_i][...]
                best_variant = data.iloc[row_i][...]
                especial_thing = data.iloc[row_i][...]
                decorations = data.iloc[row_i][...]
                best_gift = data.iloc[row_i][...]
                film = data.iloc[row_i][...]
                meal = data.iloc[row_i][...]
                people_count = data.iloc[row_i][...]
                f.write(f'Отправитель: {guy}, --> {gifted_name}\n')
                f.write('###########################################\n')
                f.write(config.task_message.format(gifted_name=gifted_name,
                                                   address=address,
                                                   index=index,
                                                   best_variant=best_variant,
                                                   especial_thing=especial_thing,
                                                   decorations=decorations,
                                                   best_gift=best_gift,
                                                   film=film,
                                                   meal=meal,
                                                   people_count=people_count))
                f.write('###########################################\n\n')

    def write_pairs_to_table(self):
        """
        Updates the table with the data from your table with pair-creations.
        You need to make sure you have the correct column 'send_to_id'.
        :return: None
        """
        data = pd.read_excel(self._path)
        self.get_people_from_doc()
        self.compare_people()
        for i, k in zip(range(len(self._pairs)), self._pairs.keys()):
            data.at[i, 'vk_id'] = k
            data.at[i, 'send_to_id'] = self._pairs[k]
        try:
            with pd.ExcelWriter(self._path, engine='openpyxl', mode='w') as writer:
                data.to_excel(writer, sheet_name='Sheet', index=False)
            print(f'Table successfully generated to the "{self._path}".')
        except (PermissionError, FileExistsError, FileNotFoundError):
            print("You do not have permission to write the file. Please try again.")

    def migrate_data_to_sqlite(self):
        data = pd.read_excel(self._path)
        m = DBMigration('./data/database.db')
        for i, record in data.iterrows():
            m.add_user(record['vk_id'], record['send_to_id'], record['name'], record['address'],
                       record['post_index'], record['new_year_attr'], record['new_year_doings'],
                       record['best_gift'], record['best_film'], record['best_song'],
                       record['best_dish'], record['best_flashback'], record['decorations'],
                       record['rabbit_gift'])


if __name__ == "__main__":
    generator = Generator()
    # ids = generator.get_people_from_doc()
    # pairs = generator.compare_people()
    # generator.write_pairs_to_table()
    generator.migrate_data_to_sqlite()

