from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from other.texts import lexicon
from database import *
from config.config import load_config
from app.kb import all_chapters, all_topics

router = Router()# Инициализация роутера для обычных пользователей

config = load_config()# Подключение конфигурационного файла


# Обработчик сообщений, который выводит текст после /start
@router.message(CommandStart())
async def start_message(message: Message):
    await message.answer(text=lexicon['/start'])


# Убирает клавиатуру
@router.message(Command(commands='remove'))
async def remove_kb(message: Message):
    await message.answer(text='229', reply_markup=ReplyKeyboardRemove())
    

# Выводит информацию с помощью
@router.message(Command(commands='help'))
async def help_message(message: Message):
    await message.answer(text=lexicon['/help'])


# Обработчик команд, который выводит информацию о записи по названию темы после команды /search
@router.message(Command(commands='search'))
async def search_theme(message: Message):
    user_text = message.text.split('/search')[1]# Сохраняет слово или фразу в переменную после команды /search
    user_text = user_text.strip()# Удаляет пробелы
    # Проверяет есть ли тема в бд с названием, которое ввел пользователь
    # Если есть, то выводится фотография, глава - тема, описание темы.
    # Если такой темы нет, то выводится соответсвующее сообщение
    if check(user_text):
        data = select_data(user_text)
        await message.answer_photo(photo=data[3], caption=f'{data[0]} - {data[1]}\n\n{data[2]}')
    else:
        await message.answer(text='Нет такой темы')


@router.message(Command(commands='dsearch'))
async def dsearch(message: Message):
    keyword = message.text.split('/dsearch')[1].strip()

    if not keyword:
        await message.reply("Пожалуйста, укажите ключевое слово после команды /dsearch")
        return

    results = deep_search(keyword)

    if results:
        response = "Результаты поиска:\n\n"
        for result in results:
            response += f"Глава: {result[0]}\nТема: {result[1]}\n\n"
    else:
        response = "По вашему запросу ничего не найдено."
    await message.reply(text=response)


# Команда, которая выводит инлайн-клавиатуру со всеми главами, которые есть в бд, в три ряда
@router.message(Command(commands='chapters'))
async def chapters(message: Message):
    keyboard_chapters = all_chapters(3)
    await message.answer(text='Список глав:', reply_markup=keyboard_chapters)


# Обработчик, который принимает данные с кнопок, которые были получены с клавиатуры chapters,
# И выводит клавиатуру с темами соответсвующей главы
@router.callback_query(F.data.startswith('chapter:'))
async def topics(callback: CallbackQuery):
    chapter = callback.data.split(":")[1]
    keyboard_topics = all_topics(chapter, 3)
    await callback.message.edit_text(text='Теперь выберите тему', reply_markup=keyboard_topics)


# Обработчик, который принимает значения кнопок, который не попали в прошлые два фильтра.
# Выводит информацию о теме по нажатию кнопки
@router.callback_query()
async def desc(callback: CallbackQuery):
    user_choice = callback.data
    data = select_data(user_choice)
    await callback.message.answer_photo(photo=data[3], caption=f'{data[0]} - {data[1]}\n\n{data[2]}')
