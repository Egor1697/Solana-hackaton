import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ВСТАВЬТЕ СВОЙ ТОКЕН СЮДА (получите у @BotFather)
TOKEN = "8140462221:AAFvuEUvkEB1y4BrPtUWYVFlP8V_jCXbQno"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Имитация данных (в реальном проекте это будет браться из Solana)
ASSETS = {
    "tractor_01": {
        "name": "Трактор МТЗ-80 (с. Мамлютка)",
        "price": 1000, # цена за 1 долю в тенге/SOL
        "total": 1000,
        "sold": 452
    }
}

USER_SHARES = {} # Здесь храним, кто что купил (временно)

# --- ГЛАВНОЕ МЕНЮ ---
def main_menu():
    buttons = [
        [InlineKeyboardButton(text="🚜 Доступная техника", callback_data="view_assets")],
        [InlineKeyboardButton(text="💰 Мои доли", callback_data="my_portfolio")],
        [InlineKeyboardButton(text="ℹ️ О проекте AgroShare", callback_data="about")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Добро пожаловать в **AgroShare** — платформу для совместного владения агро-активами на блокчейне Solana.\n\n"
        "Здесь вы можете купить долю в реальной технике и получать доход от её аренды.",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# --- ПРОСМОТР АКТИВОВ ---
@dp.callback_query(F.data == "view_assets")
async def view_assets(callback: types.CallbackQuery):
    asset = ASSETS["tractor_01"]
    text = (
        f"📍 **Объект:** {asset['name']}\n"
        f"📈 Долей продано: {asset['sold']}/{asset['total']}\n"
        f"💎 Цена за 1 долю: {asset['price']} SOL\n\n"
        "Хотите стать совладельцем?"
    )
    
    buy_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить 1 долю", callback_data="buy_1")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(text, reply_markup=buy_button, parse_mode="Markdown")

# --- ПРОЦЕСС ПОКУПКИ (Имитация транзакции Solana) ---
@dp.callback_query(F.data == "buy_1")
async def process_buy(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # Логика "покупки"
    ASSETS["tractor_01"]["sold"] += 1
    USER_SHARES[user_id] = USER_SHARES.get(user_id, 0) + 1
    
    await callback.answer("⏳ Транзакция в блокчейне Solana...", show_alert=False)
    await asyncio.sleep(2) # Имитируем ожидание подтверждения сети
    
    await callback.message.answer(
        "✅ **Успешно!**\n\n"
        "Вы приобрели 1 долю Трактора МТЗ-80.\n"
        "Запись внесена в смарт-контракт: `Agro...8x2Y`",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "my_portfolio")
async def my_portfolio(callback: types.CallbackQuery):
    shares = USER_SHARES.get(callback.from_user.id, 0)
    await callback.message.edit_text(
        f"📊 **Ваш портфель:**\n\n"
        f"🚜 Трактор МТЗ-80: {shares} шт.\n"
        f"💵 Прогноз дохода: {shares * 50} тенге/мес",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите действие:", reply_markup=main_menu())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())