import mysql.connector
from typing import List

__author__ = 'Ido Nitay Eini'


def connect_to_db():
    # return mysql.connector.connect(host='mysql-server', database='scribble', user='ido', password='idoido')
    return mysql.connector.connect(host='127.0.0.1', database='scribble', user='ido', password='idoido')


class DbConnection:

    def execute_query(self, query):
        cursor = self.connection.cursor(buffered=True)
        cursor.execute(query)
        return cursor

    def execute_command(self, query, close=True):
        cursor = self.connection.cursor(buffered=True)
        cursor.execute(query)
        self.connection.commit()
        if close:
            cursor.close()
        else:
            return cursor

    def execute_insert_command(self, query):
        # type: (object) -> object
        cursor = self.execute_command(query, False)
        last_row_id = cursor.lastrowid
        cursor.close()
        return last_row_id

    def execute_query_native(self, query, params=()):
        cursor = self.connection.cursor(buffered=True)
        cursor.execute(query, params)
        return cursor

    def execute_command_native(self, query, params=(), close=True):
        cursor = self.connection.cursor(buffered=True)
        cursor.execute(query, params)
        self.connection.commit()
        if close:
            cursor.close()
        else:
            return cursor

    def execute_insert_command_native(self, query, params=()):

        cursor = self.execute_command_native(query, params, False)
        last_row_id = cursor.lastrowid
        cursor.close()
        return last_row_id

    def get_row_count(self, cursor):
        return cursor.rowcount

    def __init__(self):
        self.connection = connect_to_db()


def get_words_from_db() -> List[str]:
    db = DbConnection()

    cursor = db.execute_query_native("select id, word from vocabulary")

    if db.get_row_count(cursor) == 0:
        print("no data")
        cursor.close()
    else:
        words = []
        for (id, word) in cursor:
            # print(id, word)
            words.append(word)

        cursor.close()
    return words
