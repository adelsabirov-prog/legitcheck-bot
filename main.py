import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

class CheckStates(StatesGroup):
    waiting_for_product = State()
    waiting_for_photos = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Я тестовый помощник Legit·Check.\n\n"
        "Что будем проверять? Напиши бренд, название продукта и тип упаковки.\n"
        "*(Например: Крем Dior в банке, Сыворотка с пипеткой)*"
    )
    await state.set_state(CheckStates.waiting_for_product)

@router.message(CheckStates.waiting_for_product)
async def process_product_name(message: Message, state: FSMContext):
    product_name = message.text
    await state.update_data(product=product_name)
    
    instruction = (
        f"Отлично, проверяем: *{product_name}*\n\n"
        "Для анализа мне нужны фото:\n"
        "1. Коробка со всех сторон\n"
        "2. Сам продукт (спереди, сзади, дно с батч-кодом)\n"
        "3. Текстура (макро на белом листе)\n\n"
        "⚠️ **ВАЖНО:** Прикрепляй фото **КАК ДОКУМЕНТ (ФАЙЛ)** через скрепку 📎\n"
        "Обычные фото Telegram сжимает, и алгоритм не увидит детали.\n\n"
        "Присылай фото по одному или архивом. Когда закончишь, напиши «Готово»."
    )
    await message.answer(instruction, parse_mode="Markdown")
    await state.set_state(CheckStates.waiting_for_photos)

@router.message(CheckStates.waiting_for_photos, F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT}))
async def process_photo(message: Message, state: FSMContext):
    file_type = "документ (файл)" if message.document else "обычное фото"
    
    await message.answer(
        "⏳ Анализирую качество снимков (тестовый режим Гейткипера)...\n\n"
        f"✅ Принято: {file_type}\n"
        "⚠️ *Тестовое предупреждение:* В реальном режиме я бы проверил резкость батч-кода и отсутствие бликов.\n"
        "Продолжай присылать фото или напиши «Готово», чтобы завершить сбор."
    )

@router.message(CheckStates.waiting_for_photos, F.text.lower() == "готово")
async def finish_collection(message: Message, state: FSMContext):
    user_data = await state.get_data()
    product = user_data.get("product", "Неизвестный продукт")
    
    await message.answer(
        f"📦 Сбор фото для *{product}* завершен.\n\n"
        "🟢 **Тестовый вердикт Гейткипера:** Качество фото достаточное для запуска алгоритма.\n\n"
        "💰 В реальном боте сейчас появилась бы кнопка: *[Оплатить 500 ₽]*\n"
        "После оплаты нейросеть сгенерировала бы полный отчет по 6 деталям."
    )
    await state.clear()

async def main():
    print(" Бот запущен на PythonAnywhere!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
