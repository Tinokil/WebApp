from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from pathlib import Path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import db
from other import get_logger, bot
import markups as mk
from locales.locate import tm

logger = get_logger(__name__)
router = Router()

@router.message(CommandStart())
async def start(message: Message):
    logger.info(f'Введена команда /start - {message.chat.id}')
    if await db.check_user(message.chat.id):
        text = await tm.get("user.texts.start", message.chat.id)
        markup = await mk.create_keyboard("user.btns.start", message.chat.id)
        await message.answer(text, reply_markup=markup)
    else:
        base_dir = Path(__file__).parent.parent
        image_path = base_dir / "assets" / "start.png"
        if not image_path.exists():
            logger.warning(f"Изображение {image_path} не найдено")
            image_path = base_dir / "assets" / "black.png"
        markup = await mk.choose_lang()    
        await message.answer_photo(photo=FSInputFile(image_path), caption="Выберите язык/Choose Language:", reply_markup=markup)

    