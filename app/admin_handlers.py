from aiogram import F, Router
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import CallbackQuery, Message, PhotoSize
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

from filters.admin_ids import AdminIdsFilter
from config.config import load_config
from other.texts import lexicon, admin_lexicon, system_lexicon
from app.kb import create_keyboard
from database import *
from filters.check_name_descr import check_name_descr


redis = Redis(host='localhost')

storage = RedisStorage(redis=redis)

config = load_config()

admin_router = Router()
admin_router.message.filter(AdminIdsFilter(config.tg_bot.admin_ids))

    
class FSMFillForm(StatesGroup):
    waiting_chapter = State()
    waiting_name = State()
    waiting_description = State()
    waiting_photo = State()
    waiting_appeal = State()


class FSMEdit(StatesGroup):
    chapter_choice = State()
    chapter = State()
    name_choice = State()
    name = State()
    text = State()


@admin_router.message(CommandStart(), StateFilter(default_state))
async def process_start(message: Message):
    await message.answer(text=lexicon['/start'])
    await message.answer(text=admin_lexicon['/start'])


@admin_router.message(Command(commands="help"), StateFilter(default_state))
async def process_help(message: Message):
    await message.answer(text=admin_lexicon['/help'])


@admin_router.message(Command(commands="help"), ~StateFilter(default_state))
async def process_help(message: Message):
    await message.answer(text=admin_lexicon['/help'])


@admin_router.message(Command(commands='chanel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text=system_lexicon['/chanel']
    )


@admin_router.message(Command(commands='chanel'), ~StateFilter(default_state))
async def process_chanel_command_state(message: Message, state: FSMContext):
    await message.answer(text=system_lexicon['/chanel'])
    await state.clear()


@admin_router.message(Command(commands='post'), StateFilter(default_state))
async def process_quest(message: Message, state: FSMContext):
    await message.answer(text=system_lexicon['/post_1'])
    await state.set_state(FSMFillForm.waiting_chapter)


@admin_router.message(StateFilter(FSMFillForm.waiting_chapter), F.text)
async def process_waiting_chapter(message: Message, state: FSMContext):
    user_chapter = message.text
    if check_name_descr(user_chapter.lower()):
        await message.answer(text=system_lexicon['matuki'])
        await state.clear()
    else:
        await state.update_data(chapter=message.text)
        await message.answer(text="Спасибо\n\nТеперь отправьте название темы")
        await state.set_state(FSMFillForm.waiting_name)


@admin_router.message(StateFilter(FSMFillForm.waiting_chapter))
async def warning_not_description(message: Message):
    await message.answer(text="Попробуйте еще раз написать название главы")


@admin_router.message(StateFilter(FSMFillForm.waiting_name), F.text)
async def process_waiting_name(message: Message, state: FSMContext):
    user_text = message.text
    if check_name_descr(user_text.lower()):
        await message.answer(text="В имени содержаться недопустимые слова или команды")
        await state.clear()
    elif not (check(user_text)):
        await state.update_data(name=message.text)
        await message.answer(text="Спасибо\n\nТеперь отправьте описание")
        await state.set_state(FSMFillForm.waiting_description)
    else:
        await message.answer(text='Такая тема уже есть, повторите свой запрос\n/post')
        await state.clear()


@admin_router.message(StateFilter(FSMFillForm.waiting_name))
async def warning_not_description(message: Message):
    await message.answer(text="Попробуйте еще раз написать название темы")


@admin_router.message(StateFilter(FSMFillForm.waiting_description), F.text)
async def process_waiting_description(message: Message, state: FSMContext):
    user_description = message.text
    if len(user_description) > 1000:
        await message.answer(text='Слишком длинное сообщение, попробуйте сократить текст до 1000 символов')
    else:
        if check_name_descr(user_description.lower()):
            await message.answer(text="В описании темы содержаться недопустимые слова или команды")
            await state.clear()
        else:
            await state.update_data(descripthion=user_description)
            await message.answer(text="Спасибо\n\nТеперь отправьте фото")
            await state.set_state(FSMFillForm.waiting_photo)


@admin_router.message(StateFilter(FSMFillForm.waiting_description))
async def warning_not_description(message: Message):
    await message.answer(text="Попробуйте еще раз написать содержание темы")


@admin_router.message(StateFilter(FSMFillForm.waiting_photo), F.photo[-1].as_('largest_photo'))
async def process_photo(message: Message, state: FSMContext, largest_photo: PhotoSize):
    await state.update_data(photoId=largest_photo.file_id)
    await message.answer(text="Добавить/внести изменения?", reply_markup=create_keyboard("Добавить", "Отмена"))
    await state.set_state(FSMFillForm.waiting_appeal)


@admin_router.message(StateFilter(FSMFillForm.waiting_photo))
async def warning_photo(message: Message):
    await message.answer(text="Попробуйте еще раз отправить фото")


@admin_router.callback_query(StateFilter(FSMFillForm.waiting_appeal), F.data.in_(['yes', 'no']))
async def process_appeal(callback: CallbackQuery, state: FSMContext):
    if callback.data == "yes":
        state_data = await state.get_data()
        insert_blob(state_data['chapter'], state_data['name'], state_data['descripthion'], state_data["photoId"])
        await callback.message.edit_text(text="Запись успешно добавлена")
        await state.clear()
    else:
        await state.clear()
        await callback.message.edit_text(text="Добавление отменено")


@admin_router.message(StateFilter(FSMFillForm.waiting_appeal))
async def warning_appeal(message: Message):
    await message.answer(text="warning_appeal")


@admin_router.message(Command(commands="showquest"), StateFilter(default_state))
async def process_showquest(message: Message): 
    last_post = check_value_table()
    if last_post:
        date_post = last_post[4].split()
        day_post = date_post[0]
        time_post = date_post[1]
        if last_post:
            await message.answer_photo(
                photo=last_post[3],
                caption=f'Глава: {last_post[0]}\nТема: {last_post[1]}\nДата добавления: {day_post}\nВремя добавления: {time_post}\n\nТекст: {last_post[2]}'
                )
        else:
            await message.answer(text="Посты еще пока не были добавлены")
    else:
        await message.answer(text='Нет данных о последней теме')


@admin_router.message(Command(commands="delete"), StateFilter(default_state))
async def edit(message: Message):
    user_text = message.text.split('/delete')[1]
    user_text = user_text.strip()
    if delete_data(user_text):
        await message.answer(text="Запись успешно удалена")
    else:
        await message.answer(text="Что то пошло не так.\n\nВозможно такой записи нет")


@admin_router.message(Command(commands="edit"), StateFilter(default_state))
async def edit(message: Message, state: FSMContext):
    topic_name = message.text.split('/edit')[1]
    topic_name = topic_name.strip()
    if check(topic_name):
        await message.answer(text=f'Вы желаете отредактировать название главы?', reply_markup=create_keyboard('Да','Нет'))
        await state.set_state(FSMEdit.chapter_choice)
        await state.update_data(topic_name=topic_name)
    else:
        await message.answer(text="Темы с таким именем нету")

    
@admin_router.callback_query(StateFilter(FSMEdit.chapter_choice),F.data.in_(['yes', 'no']))
async def edit_chapter_choice(callback: CallbackQuery, state: FSMContext):
    if callback.data == "yes":
        await callback.message.answer(text="Отправьте новое название главы для записи")
        await state.set_state(FSMEdit.chapter)
    else:
        await state.update_data(user_chapter="")
        await state.set_state(FSMEdit.name_choice)
        await callback.message.answer(text="Вы желаете отредактировать название темы?",reply_markup=create_keyboard('Да','Нет'))


@admin_router.message(StateFilter(FSMEdit.chapter_choice))
async def warning_appeal(message: Message):
    await message.answer(text="warning_chapter_choice")


@admin_router.message(StateFilter(FSMEdit.chapter), F.text)
async def edit_chapter(message: Message, state: FSMContext):
    user_chapter = message.text
    if check_name_descr(user_chapter.lower()) == False:
        await state.update_data(user_chapter=user_chapter)
        await state.set_state(FSMEdit.name_choice)
        await message.answer(text="Вы желаете отредактировать название темы?",reply_markup=create_keyboard('Да','Нет'))
    else:
        await message.answer(text="В названии главы содержаться недопустимые слова или команды")


@admin_router.message(StateFilter(FSMEdit.chapter))
async def warning_appeal(message: Message):
    await message.answer(text="warning_chapter")


@admin_router.callback_query(StateFilter(FSMEdit.name_choice),F.data.in_(['yes', 'no']))
async def edit_name_choice(callback: CallbackQuery, state: FSMContext):
    if callback.data == "yes":
        await callback.message.answer(text="Отправьте новое название темы для записи")
        await state.set_state(FSMEdit.name)
    else:
        await state.update_data(new_topic_name="")
        await state.set_state(FSMEdit.text)
        await callback.message.answer(text=f'Отправьте описание (отдельно), фото (отдельно), или все вместе (одним сообщением).\n\nИ тогда изменения будут внесены')


@admin_router.message(StateFilter(FSMEdit.name_choice))
async def warning_appeal(message: Message):
    await message.answer(text="warning_name_choice")


@admin_router.message(StateFilter(FSMEdit.name), F.text)
async def edit_name(message: Message, state: FSMContext):
    new_topic_name = message.text
    if check_name_descr(new_topic_name) == False:
        await state.update_data(new_topic_name=new_topic_name)
        await state.set_state(FSMEdit.text)
        await message.answer(text=f'Отправьте описание (отдельно), фото (отдельно), или все вместе (одним сообщением).\n\nИ тогда изменения будут внесены')
    else:
        await message.answer(text="В названии темы содержаться недопустимые слова или команды")


@admin_router.message(StateFilter(FSMEdit.name))
async def warning_appeal(message: Message):
    await message.answer(text="warning_name")


@admin_router.message(StateFilter(FSMEdit.text))
async def edit_appeal(message: Message, state: FSMContext):
    state_data = await state.get_data()
    elements_db = []
    for key in state_data.keys():
        elements_db.append(state_data[key])
    if message.text:
        description = message.text
        elements_db.append(description)
        if update_data(elements_db):
            await message.answer(text="Данные успешно изменены")
        else:
            await message.answer(text="Что то пошло не так, поробуйте снова")
        await state.clear()

    elif (message.photo and message.caption) != None:
        description = message.caption
        photo = message.photo[-1].file_id
        elements_db.append(description)
        elements_db.append(photo)
        if update_data(elements_db) and check_name_descr(description.lower()) == False:
            await message.answer(text="Данные успешно изменены")
        else:
            await message.answer(text="Что то пошло не так, поробуйте снова")
        await state.clear()

    elif (message.photo and message.caption) == None:
        description = select_data(elements_db[0])[2]
        photo = message.photo[-1].file_id
        elements_db.append(description)
        elements_db.append(photo)
        if update_data(elements_db):
            await message.answer(text="Данные успешно изменены")
        else:
            await message.answer(text="Что то пошло не так, поробуйте снова")
        await state.clear()

    else:
        await message.answer(text="Вы отрпавили не фото и не текст.\n\nПожалуйста повторите попытку")
