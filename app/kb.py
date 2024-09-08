from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database import get_topic, get_chapter


# Функция, которая создает инлайн-клавиатуру с кнопками Да и Нет.
# Возвращает готовую клавиатуру
def create_keyboard(text_first, text_second) -> InlineKeyboardMarkup:
    yes_button = InlineKeyboardButton(text=text_first, callback_data='yes')
    no_button = InlineKeyboardButton(text=text_second, callback_data="no")
    keyboard: list[list[InlineKeyboardButton]] = [[yes_button, no_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


# Функция, которая принимает количество столбиков и возвращает инлайн-клавиатуру
def all_chapters(width: int) -> InlineKeyboardMarkup:
    kb_builder_chapters = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    topics = get_chapter()# В переменную сохраняются все названия глав
    # В переменную с кнопками добавляются кнопки с именами соответсвтующих глав и колбек датой, которая начинается с chapter:
    for button in topics:
        buttons.append(InlineKeyboardButton(text=button[0], callback_data=f"chapter:{button[0]}"))

    kb_builder_chapters.row(*buttons, width=width)

    return kb_builder_chapters.as_markup()


# Функция, которая выводит клавиатуру со всеми темами.
# Принимает название главы и количество столбиков
def all_topics(chapter, width: int) -> InlineKeyboardMarkup:
    all_Topics = get_topic(chapter)
    kb_builder_topics = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    for button in all_Topics:
        buttons.append(InlineKeyboardButton(text=button[0], callback_data=button[0]))

    kb_builder_topics.row(*buttons, width=width)

    return kb_builder_topics.as_markup()
