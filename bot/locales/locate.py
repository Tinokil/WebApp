import json
import aiofiles
from pathlib import Path
from typing import Any
from functools import lru_cache
from string import Template

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import db


class TextManager:
    def __init__(self):
        self.locale_dir = Path(__file__).parent
        self._cache = {}

    async def _load_locale(self, lang: str) -> None:
        """Загрузка языкового файла"""
        file_path = self.locale_dir / f"{lang}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл отсутствует: {file_path}")
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                self._cache[lang] = json.loads(content)
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки {lang}: {str(e)}")

    @lru_cache(maxsize=256)
    def _resolve_text(self, lang: str, key: str) -> str:
        """Быстрый поиск текста с кэшированием"""
        data = self._cache.get(lang, {})
        for part in key.split('.'):
            data = data.get(part, {})
            if not data:
                return f"⚠️ {key}"
        return data if isinstance(data, str) else f"⚠️ {key}"

    async def get(self, key: str, user_id: int, **replacements: Any) -> str:
        """Получение локализованного значения"""
        try:
            lang = await db.get_user_lang(user_id)
            if lang not in self._cache:
                try:
                    await self._load_locale(lang)
                except Exception as e:
                    if lang != "ru":
                        await self._load_locale("ru")
                    else:
                        return "⚠️ Ошибка загрузки"
            data = self._cache.get(lang, self._cache.get("ru", {}))
            try:
                for key_part in key.split('.'):
                    data = data[key_part]
                if isinstance(data, str):
                    if replacements:
                        try:
                            return data.format(**replacements)
                        except (KeyError, ValueError):
                            return Template(data).safe_substitute(**replacements)
                    return data
                return data
                
            except KeyError:
                return f"⚠️ Ключ '{key}' не найден"
                
        except Exception as e:
            return "⚠️ Системная ошибка"

    async def reload(self) -> None:
        """Перезагрузка данных локализации"""
        async with self._lock:
            self._cache.clear()
            self._resolve_text.cache_clear()
            
            
tm = TextManager()
            