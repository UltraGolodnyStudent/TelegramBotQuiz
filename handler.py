from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F

from config import API_TOKEN
from utils import new_quiz, get_question
from dataBase import get_quiz_index, update_quiz_index, get_quiz_score
from quizText import quiz_data

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

# При ответе на вопрос
@dp.callback_query()
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Получение текущего счета из словаря состояний пользователя
    current_quiz_score = await get_quiz_score(callback.from_user.id)

    correct_option = quiz_data[current_question_index]['correct_option']
    correct_answer = quiz_data[current_question_index]['options'][correct_option]

    if(callback.data == correct_answer):
        await callback.message.answer("Верно!")
        current_question_index = await get_quiz_index(callback.from_user.id)
        current_question_index += 1
        current_quiz_score += 1
        await update_quiz_index(callback.from_user.id, current_question_index, current_quiz_score)
    else:
        await callback.message.answer(f"Неправильно. Правильный ответ: {correct_answer}")
        await callback.message.answer(f"Ваш ответ: {callback.data}")
        current_question_index += 1
        await update_quiz_index(callback.from_user.id, current_question_index, current_quiz_score)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        await callback.message.answer(f"Ваша статистика (из 10): {current_quiz_score}")
