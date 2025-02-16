import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
import os

load_dotenv()  # Загружаем переменные окружения из .env
TOKEN =("7909793879:AAHTSt1EtVXzDdR5JHTToqfyunhhp_DxIs4")  # Твой Telegram токен
OPERATOR_CHAT_ID = os.getenv("OPERATOR_CHAT_ID")  # ID чата с оператором

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

# Определяем состояния
class VisaForm(StatesGroup):
    citizenship = State()
    oman_visa = State()
    visa_expiry = State()
    departure_date = State()
    location = State()
    visa_type = State()
    people_count = State()
    car_choice = State()
    confirmation = State()

# Стартовый обработчик
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Обновить визу"))
    await message.answer("Привет! Хотите обновить визу?", reply_markup=keyboard)

# Начало опроса
@dp.message_handler(lambda message: message.text == "Обновить визу")
async def ask_citizenship(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Казахстан", "Украина", "Россия", "Киргизстан", "Другая страна")
    await message.answer("Выберите ваше гражданство:", reply_markup=keyboard)
    await VisaForm.citizenship.set()

@dp.message_handler(state=VisaForm.citizenship)
async def ask_oman_visa(message: types.Message, state: FSMContext):
    await state.update_data(citizenship=message.text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Да", "Нет")
    await message.answer("Нужна ли вам виза в Оман? (190 руб)", reply_markup=keyboard)
    await VisaForm.oman_visa.set()

@dp.message_handler(state=VisaForm.oman_visa)
async def ask_visa_expiry(message: types.Message, state: FSMContext):
    await state.update_data(oman_visa=message.text)
    await message.answer("Укажите дату окончания вашей визы (дд-мм-гггг):")
    await VisaForm.visa_expiry.set()

@dp.message_handler(state=VisaForm.visa_expiry)
async def ask_departure_date(message: types.Message, state: FSMContext):
    await state.update_data(visa_expiry=message.text)
    await message.answer("Укажите желаемую дату выезда на обновление (дд-мм-гггг):")
    await VisaForm.departure_date.set()

@dp.message_handler(state=VisaForm.departure_date)
async def ask_location(message: types.Message, state: FSMContext):
    await state.update_data(departure_date=message.text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Дубай", "Абу-Даби", "Шарджа", "Другой")
    await message.answer("Выберите вашу локацию:", reply_markup=keyboard)
    await VisaForm.location.set()

@dp.message_handler(state=VisaForm.location)
async def ask_visa_type(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("30 дней", "60 дней", "90 дней", "Обновление на 30 без выезда")
    await message.answer("Выберите тип визы:", reply_markup=keyboard)
    await VisaForm.visa_type.set()

@dp.message_handler(state=VisaForm.visa_type)
async def ask_people_count(message: types.Message, state: FSMContext):
    await state.update_data(visa_type=message.text)
    await message.answer("Сколько вас человек?")
    await VisaForm.people_count.set()

@dp.message_handler(state=VisaForm.people_count)
async def ask_car_choice(message: types.Message, state: FSMContext):
    await state.update_data(people_count=message.text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Мерседес - 5000 руб", "Камри - 3000 руб", "Автобус - 1500 руб")
    await message.answer("Выберите транспорт для поездки:", reply_markup=keyboard)
    await VisaForm.car_choice.set()

@dp.message_handler(state=VisaForm.car_choice)
async def confirm_booking(message: types.Message, state: FSMContext):
    await state.update_data(car_choice=message.text)
    data = await state.get_data()
    
    # Отправка данных оператору
    lead_info = f"""
🚀 Новый запрос на обновление визы:

🌍 Гражданство: {data['citizenship']}
🛂 Виза в Оман: {data['oman_visa']}
📅 Окончание визы: {data['visa_expiry']}
📆 Дата выезда: {data['departure_date']}
📍 Локация: {data['location']}
📝 Тип визы: {data['visa_type']}
👥 Количество людей: {data['people_count']}
🚗 Выбранный транспорт: {data['car_choice']}

Свяжитесь с клиентом!
"""
    await bot.send_message(OPERATOR_CHAT_ID, lead_info)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Подтвердить бронь")
    await message.answer("Спасибо за ответы! Нажмите, чтобы подтвердить бронь.", reply_markup=keyboard)
    await VisaForm.confirmation.set()

@dp.message_handler(state=VisaForm.confirmation)
async def send_whatsapp_group(message: types.Message, state: FSMContext):
    await message.answer("Бронь подтверждена! Вот ссылка на WhatsApp-группу: https://wa.me/123456789")
    await state.finish()

# Запуск бота
async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())