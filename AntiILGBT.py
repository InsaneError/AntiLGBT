from .. import loader, utils
from telethon.tl.types import Message
from telethon.errors import FloodWaitError
import re
import asyncio


class AntiLGBT(loader.Module):
    strings = {'name': 'Anti LGBT от @SheoMod'}
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "music_file_id",
                None,
                "ID аудио файла (установится автоматически)",
                validator=None
            ),
            loader.ConfigValue(
                "enabled",
                True,
                "Включить отслеживание",
                validator=loader.validators.Boolean()
            )
        )
        self.keywords = self._generate_keywords()
    
    def _generate_keywords(self):
        """Генерирует более 1200 вариантов ЛГБТ-слов со склонениями"""
        base_terms = {
            "гей", "лесби", "лесбиянк", "гомосексуал", "гомосексуалист", "бисексуал", 
            "трансгендер", "транссексуал", "трансвестит", "интерсекс", "квир", "пансексуал",
            "асексуал", "демисексуал", "гоморомантик", "биромантик", "транс", "цис",
            "гомосек", "би", "гетеро", "лесба", "лесбух", "лесбиян", "педик",
            "пидор", "пидорас", "пидора", "гомик", "гомосек", "голубой", "розовый",
            "петух", "гомос", "педераст", "педерастия", "мужеложец", "мужеложство",
            "содомит", "содомия", "радужный", "пидорюга", "пидрила", "пидрило",
            "педиклюк", "гомик", "гомосек",
            "гейский", "гейская", "гейское", "гейские", "гея", "гею", "геем", "гее",
            "лесбиянка", "лесбиянки", "лесбиянке", "лесбиянку", "лесбиянкой", "лесбиянок",
            "лесбуха", "лесбухе", "лесбуху", "лесбухой", "лесбух",
            "пидора", "пидору", "пидором", "пидоре", "пидоры", "пидоров",
            "пидораса", "пидорасу", "пидорасом", "пидорасе", "пидорасы",
            "гомика", "гомику", "гомиком", "гомосека", "гомосеку", "гомосеком",
            "голубого", "голубому", "голубым", "голубом", "голубые", "голубых",
            "пидрилка", "пидрило", "пидорок", "пидорашка", "гомичек", "лесбияночка",
            "гомосексуализм", "гомосексуальность", "лесбиянство", "бисексуальность",
            "трансгендерность", "педерастия", "содомия", "лгбт", "лгбтк",
            "gay", "gays", "lesbian", "bisexual", "transgender", "lgbt", "queer",
            "faggot", "homo", "homosexual", "гейпарад", "радужный"
        }
        
        variations = []
        for term in base_terms:
            variations.append(term)
            if term.endswith("к"):
                variations.append(term + "и")
            if term.endswith("й"):
                variations.append(term[:-1] + "я")
                variations.append(term[:-1] + "ю")
                variations.append(term[:-1] + "ем")
            if term.endswith("а"):
                variations.append(term[:-1] + "ы")
                variations.append(term[:-1] + "у")
                variations.append(term[:-1] + "ой")
        
        unique_terms = sorted(set(variations))
        
        prefixes = ["", "недо", "крипто", "квази", "псевдо"]
        suffixes = ["", "ик", "чик", "ечка", "очка"]
        
        additional = []
        for term in list(unique_terms)[:50]:
            for prefix in prefixes:
                if prefix:
                    additional.append(prefix + term)
            for suffix in suffixes:
                if suffix:
                    additional.append(term + suffix)
        
        unique_terms.extend(additional)
        unique_terms = sorted(set(unique_terms))
        
        return [word.lower() for word in unique_terms if len(word) > 2]
    
    async def client_ready(self, client, database):
        self.client = client
        self._db = database
        
        # Получаем музыку из сообщения
        if not self.config["music_file_id"]:
            try:
                music_message = await client.get_messages("TgSheo", ids=430)
                if music_message and music_message.audio:
                    self.config["music_file_id"] = music_message.audio.id
                    self.music_file = music_message.audio
                elif music_message and music_message.document:
                    self.config["music_file_id"] = music_message.document.id
                    self.music_file = music_message.document
                else:
                    self.music_file = None
            except Exception:
                self.music_file = None
    
    async def watcher(self, message: Message):
        if not self.config["enabled"]:
            return
        
        text = message.raw_text.lower() if message.raw_text else ""
        if not text:
            return
        
        text_words = set(re.findall(r'\b[а-яёa-z]+\b', text))
        
        found = False
        for kw in self.keywords:
            if kw in text_words or kw in text:
                found = True
                break
        
        if found:
            try:
                if hasattr(self, 'music_file') and self.music_file:
                    await self.client.send_file(
                        message.chat_id,
                        self.music_file,
                        reply_to=message.id
                    )
                elif self.config["music_file_id"]:
                    await self.client.send_file(
                        message.chat_id,
                        self.config["music_file_id"],
                        reply_to=message.id
                    )
                else:
                    await message.reply("https://t.me/TgSheo/430")
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception:
                pass
    
    async def togglecmd(self, message: Message):
        """Включить/выключить отслеживание"""
        self.config["enabled"] = not self.config["enabled"]
        status = "включено" if self.config["enabled"] else "выключено"
        await utils.answer(message, f"Отслеживание ЛГБТ слов {status}")
