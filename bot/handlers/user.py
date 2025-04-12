from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message, InlineKeyboardMarkup
from pathlib import Path
from typing import Optional

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import db
from other import get_logger, bot
from locales.locate import tm
import markups as mk

logger = get_logger(__name__)
router = Router()

@router.callback_query(F.data.startswith('choose_lang-'))
async def start(call: CallbackQuery):
    logger.info(f'Регистрация - {call.message.chat.id}')
    await db.add_user(call.message.chat.id, call.data.split('-')[1])
    text = await tm.get("user.texts.start", call.message.chat.id)
    markup = await mk.create_keyboard("user.btns.start", call.message.chat.id)
    await call.message.edit_caption(caption=text, reply_markup=markup)
    

@router.callback_query(F.data.startswith('scene-'))
async def start(call: CallbackQuery):
    scene = call.data.split("-")[1]
    logger.info(f'Открытие сцены {scene} - {call.message.chat.id}')
    text = await tm.get(f"user.texts.{scene}", call.message.chat.id)
    markup = await mk.create_keyboard(f"user.btns.{scene}", call.message.chat.id)
    await call.message.delete()
    
    base_dir = Path(__file__).parent.parent
    image_path = base_dir / "assets" / f"{scene}.png"
    if not image_path.exists():
        logger.warning(f"Изображение {image_path} не найдено")
        image_path = base_dir / "assets" / "black.png"
    
    await send_photo_with_caption(message=call.message, photo=FSInputFile(image_path), caption=text, reply_markup=markup)
    
    
@router.callback_query(F.data == 'pass')
async def pass_handler(call: CallbackQuery):
    await call.answer()
    
    
async def send_photo_with_caption(message: Message, photo: FSInputFile, caption: str, reply_markup: Optional[InlineKeyboardMarkup] = None, max_caption_length: int = 1024) -> None:
    """Отправляет фото с подписью, автоматически разделяя длинные подписи"""
    try:
        if len(caption) <= max_caption_length:
            await message.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup)
            return
        
        words = caption.split()
        first_part = []
        second_part = []
        current_length = 0

        for word in words:
            if current_length + len(word) + len(first_part) <= max_caption_length:
                first_part.append(word)
                current_length += len(word)
            else:
                second_part.append(word)
        
        first_text = ' '.join(first_part)
        second_text = ' '.join(second_part)
        await message.answer_photo(photo=photo, caption=first_text)
        if second_text:
            await message.answer(text=second_text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await message.answer("Произошла ошибка, мы уже работаем над ней")
    