import sqlite3
import time
import datetime
from pathlib import Path
from typing import Optional, List

import models


class DataConn:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        if exc_val:
            raise


db_title = Path(__file__).parent / 'db.db'


class Payments:
    @staticmethod
    def get_user_payment(user_id: int) -> models.Payment:
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT * FROM payments WHERE `user_id` = ?'
            c.execute(sql, (user_id,))
            return models.Payment(**c.fetchone())


class Users:
    @staticmethod
    def register_user(user_id: int):
        if not Users.get_user(user_id):
            with DataConn(db_title) as conn:
                c = conn.cursor()
                sql = 'INSERT INTO `users` (`user_id`, `jointime`) VALUES (?, ?)'
                c.execute(sql, (user_id, int(time.time())))
                conn.commit()

    @staticmethod
    def get_user(user_id: int) -> Optional[models.User]:
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT * FROM `users` WHERE `user_id` = ?'
            c.execute(sql, (user_id,))
            r = c.fetchone()
            if r:
                print(models.User(**r))
                return models.User(**r)
            else:
                return None

    @staticmethod
    def set_kicktime(user_id: int):
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'UPDATE `users` SET `kicktime` = ? WHERE `user_id` = ?'
            c.execute(sql, (int(time.time() + Settings.get_days() * 24 * 60 * 60), user_id))
            conn.commit()

    @staticmethod
    def set_kicktime_demo(user_id: int):
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'UPDATE `users` SET `kicktime` = ? WHERE `user_id` = ?'
            c.execute(sql, (int(time.time() + 10 * 60), user_id))
            conn.commit()

    @staticmethod
    def set_day_use(user_id: int):
        with DataConn(db_title) as conn:
            print('s')
            c = conn.cursor()
            now = datetime.datetime.now()
            print('i')  
            sql = 'UPDATE `users` SET `access_demo` = ? WHERE `user_id` = ?'
            c.execute(sql, ((now.day), user_id))
            conn.commit()

    @staticmethod
    def get_day(user_id: int) -> int:
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT `access_demo` FROM `users` WHERE `user_id` = ?'
            r = c.execute(sql, (user_id,))
            r = c.fetchone()
            return int(r[0])

         
    @staticmethod
    def get_users_to_kick() -> Optional[List[models.User]]:
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT * FROM `users` WHERE `kicktime` != 0 AND `kicktime` < ?'
            c.execute(sql, (int(time.time()),))
            r = c.fetchall()
            if r:
                res = [models.User(**i) for i in r]
            else:
                res = None
            return res


class Settings:
    @staticmethod
    def _get_settings(param: str) -> int:
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT `value` FROM `settings` WHERE `key` = ?'
            c.execute(sql, (param,))
            r = c.fetchone()
            return int(r[0])

    @staticmethod
    def _set_setting(param: str, value: int):
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'UPDATE `settings` SET `value` = ? WHERE `key` = ?'
            c.execute(sql, (value, param))
            conn.commit()

    @staticmethod
    def get_price() -> int:
        return Settings._get_settings('price')

    @staticmethod
    def get_days() -> int:
        return Settings._get_settings('days')

    @staticmethod
    def get_seconds() -> int:
        return Settings._get_settings('seconds')

    @staticmethod
    def set_price(value: int):
        Settings._set_setting('price', value)

    @staticmethod
    def set_days(value: int):
        Settings._set_setting('days', value)

    @staticmethod
    def set_seconds(value: int):
        Settings._set_setting('seconds', value)
