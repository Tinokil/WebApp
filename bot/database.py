import aiosqlite
from os import getenv, path
from other import get_logger


logger = get_logger(__name__)


class DataBase:
    def __init__(self, filename):
        self._filename = filename

    async def create_tables(self):
        """Создание таблиц"""
        try:
            conn = await self.open()
            await conn.execute("""CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER NOT NULL PRIMARY KEY,
                lang TEXT CHECK(lang IN ('ru', 'en')) NOT NULL DEFAULT 'ru'
            )""")
            
            await conn.commit()
            logger.info('Таблицы созданы')
        except Exception as e:
            logger.warning(f'Ошибка создания таблиц - {e}')
            
            
    async def check_user(self, user_id: int):
        """Проверка на регистрацию"""
        try:
            logger.info(f'Проверка на регистрацию')  
            conn = await self.open()
            cursor = await conn.execute("""SELECT 1 FROM users WHERE user_id = ?""", (user_id,))
            result = await cursor.fetchone()
            return True if result else False
        except Exception as e:
            logger.warning(f'Ошибка проверки на регистрацию - {e}')
            
    async def get_users(self):
        """Получение всех пользователей"""
        try:
            logger.info('Получение списка всех пользователей')  
            conn = await self.open()
            cursor = await conn.execute("""SELECT user_id FROM users""")
            return [a[0] for a in await cursor.fetchall()]
        except Exception as e:
            logger.warning(f'Ошибка получения пользователей - {e}')
            
    async def get_user_lang(self, user_id: int):
        """Получение языка пользователя"""
        try:
            logger.info('Получение языка пользователя')  
            conn = await self.open()
            cursor = await conn.execute("""SELECT lang FROM users WHERE user_id = ?""", (user_id,))
            result = await cursor.fetchone()
            return result[0] if result else 'ru'
        except Exception as e:
            logger.warning(f'Ошибка получения языка пользователя - {e}')   
            
    async def add_user(self, user_id: int, lang: str):
        """Добавление пользователя"""
        try:
            logger.info(f'Добавление пользователя {user_id}')
            if await db.check_user(user_id):
                return False
            conn = await self.open()
            await conn.execute("""INSERT OR IGNORE INTO users (user_id, lang) VALUES (?, ?)""", (user_id, lang))
            await conn.commit()
            return True
        except Exception as e:
            logger.warning(f'Ошибка добавления пользователя - {e}')
            
    async def open(self):
        return await aiosqlite.connect(self._filename)


db = DataBase(path.join(path.dirname(path.abspath(__file__)), getenv('DB_NAME')))
