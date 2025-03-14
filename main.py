import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

from config import API_TOKEN
from dataBase import create_table, update_quiz_index, get_quiz_index, get_quiz_score

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

DB_NAME = 'quiz_bot.db'

# Структура квиза
quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    },
    {
        'question': 'Кто такой Жак Фреско?',
        'options': ['Сказочный фокусник', 'Пытливый ум', 'Автор мемов', 'Уважаемый инженер'],
        'correct_option': 3
    },
    {
        'question': 'Когда выйдет Скайрим 6?',
        'options': ['В 2028', 'В 2029', 'Скайрим - провинция', 'Скайрим для нордов'],
        'correct_option': 2
    },
    {
        'question': 'Кто перевел слонов через Альпы?',
        'options': ['Каннибал', 'Ганнибал', 'Ультракупец', 'Сами перешли'],
        'correct_option': 1
    },
    {
        'question': 'Что в черной дыре?',
        'options': ['Мэттью Макконахи', 'Горизонт событий', 'Вселенная порядком ниже', 'Возможно сингулярность'],
        'correct_option': 3
    },
    {
        'question': 'Что нужно сделать сразу после пробуждения утром?',
        'options': ['Купить Скайрим', 'Почистить зубы', 'Приготовить завтрак', 'Съесть завтрак'],
        'correct_option': 1
    },
    {
        'question': 'Чья фраза: не смогли смириться с поражением? И куда вас это привело? Снова ко мне',
        'options': ['Преподаватель на пересдаче', 'Дональд Трамп', 'Танос', 'Майор в военкомате'],
        'correct_option': 2
    },
    {
        'question': 'Кто такой Сон Джин Ву?',
        'options': ['Известный актер', 'Известный охотник', 'Блогер', 'Корейский айдол'],
        'correct_option': 1
    },
    {
        'question': 'Что производит Nutella?',
        'options': ['Видеокарты', 'Фильмы для взрослых', 'Взрослых', 'Шоколадную пасту'],
        'correct_option': 3
    },
]


def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=option)
        )  
    builder.adjust(1)
    return builder.as_markup()


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


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    current_quiz_score = 0
    await update_quiz_index(user_id, current_question_index, current_quiz_score)
    await get_question(message, user_id)


# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)


# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())