from dataBase import update_quiz_index, get_quiz_index
from quizText import quiz_data
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=option)
        )  
    builder.adjust(1)
    return builder.as_markup()

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    current_quiz_score = 0
    await update_quiz_index(user_id, current_question_index, current_quiz_score)
    await get_question(message, user_id)

async def get_question(message, user_id):
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)
