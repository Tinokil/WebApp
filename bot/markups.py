from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from other import get_logger

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from locales.locate import tm

logger = get_logger(__name__)

async def create_keyboard(key_path: str, user_id: int) -> InlineKeyboardMarkup:
    """Создает Inline-клавиатуру по пути к кнопкам в JSON"""
    buttons_data = await tm.get(key_path, user_id)
    if isinstance(buttons_data, str) and buttons_data.startswith("⚠️"):
        return buttons_data
    try:
        rows = sorted([(int(k), v) for k, v in buttons_data.items() if k.isdigit()], key=lambda x: x[0])
        
        keyboard = []
        for row_num, row_buttons_data in rows:
            def sort_key(item):
                key = item[0]
                try:
                    return (0, int(key))
                except ValueError:
                    return (1, key)
            sorted_buttons = sorted(row_buttons_data.items(), key=sort_key)
            row = []
            for btn_key, btn_info in sorted_buttons:
                if not isinstance(btn_info, list) or len(btn_info) != 2:
                    logger.warning(f"Некорректные данные для кнопки {btn_key}: {btn_info}")
                    continue
                
                text, data = btn_info
                if data.startswith("url="):
                    url = data.split("=", 1)[1]
                    button = InlineKeyboardButton(text=text, url=url)
                else:
                    button = InlineKeyboardButton(text=text, callback_data=data)
                row.append(button)
            if row:
                keyboard.append(row)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    except Exception as e:
        logger.warning(f"Ошибка создания клавиатуры: {e}")
        return InlineKeyboardMarkup(inline_keyboard=[])
        
        
async def choose_lang() -> InlineKeyboardMarkup:
    try:
        btns = [[InlineKeyboardButton(text="RU\U0001F1F7\U0001F1FA", callback_data="choose_lang-ru"), InlineKeyboardButton(text="EN\U0001F1FA\U0001F1F8", callback_data="choose_lang-en")]]
        return InlineKeyboardMarkup(inline_keyboard=btns)
    except Exception as e:
        logger.warning(f"Ошибка: {e}")
        
        
async def payment_button(url) -> InlineKeyboardMarkup:
    try:
        btns = [[InlineKeyboardButton(text="ОПЛАТИТЬ", url=url)]]
        return InlineKeyboardMarkup(inline_keyboard=btns)
    except Exception as e:
        logger.warning(f"Ошибка: {e}")
