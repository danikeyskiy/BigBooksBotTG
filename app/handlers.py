from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from aiogram.filters import CommandStart
from peewee import DoesNotExist

import app.keyboards as kb
from app.database.models import UserInfo, Book
from app.database.requests import *
from backup import create_backup
from app.exporters import *

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        user = UserInfo.get(tg_id=message.from_user.id)
        if user.role == 'admin':
            await message.answer('Здравствуйте, администратор!\n' 
                                 'Чем могу помочь вам сегодня?', 
                                 reply_markup=kb.admin)
        else:
            await message.answer('Здравствуйте! 📚\n' 
                                 'Я — ваш книжный помощник! Помогу найти любую книгу: классику, бестселлеры, '
                                 'научную литературу или что-то новое и необычное. ' 
                                 'Просто отправьте название книги, и я найду её для вас.\n' 
                                 'Готовы начать поиски? 🔍📖', reply_markup=kb.main)

    except DoesNotExist:
        UserInfo.create(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            role='user'
        )
        await message.answer('Добро пожаловать! 📚\n' 
                             'Я добавил вас в базу данных и готов помочь найти любую книгу. ' 
                             'Просто отправьте название книги, и я найду её для вас.\n' 
                             'Готовы начать поиски? 🔍📖', reply_markup=kb.main)

@router.message(F.text == 'Найти книгу')
async def search(message: Message):
    await message.answer('Напишите название книги')

@router.message(F.text == 'Предложить книгу')
async def suggestion(message: Message):
    await message.answer('Отправьте название книги ответом на это сообщение')
    
@router.message(F.text == 'Посмотреть предложения пользователей')
async def check_suggestion(message: Message):
    user = UserInfo.get(tg_id=message.from_user.id)
    if user.role != 'admin':
        await message.answer('У вас нет прав для выполнения этой команды')
        return
    
    suggestions = Suggestions.select().order_by(Suggestions.suggestion_date)
    
    response = 'Предложения пользователей:\n\n'
    buttons = []
    for suggestion in suggestions:
        user = suggestion.user_id
        response += (f"Предложение {suggestion.id}:\n"
                     f"Пользователь @{user.username}\n"
                     f"Дата: {suggestion.suggestion_date}\n"
                     f"Предложение: {suggestion.suggestion_text}\n\n")
        buttons.append([InlineKeyboardButton(
            text=f"[{suggestion.id}] Добавлено ✅",
            callback_data=f"delete_suggestion:{suggestion.id}"
        )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)   
    await message.answer(response, reply_markup=keyboard)
    
@router.message(F.text == 'Выгрузить данные из БД')
async def export_data(message: Message):
    user = UserInfo.get(tg_id=message.from_user.id)
    if user.role != 'admin':
        await message.answer('У вас нет прав для выполнения этой команды')
        return

    models = {
        "Users": UserInfo,
        "Books": Book,
        "Downloads": Downloads,
        "Suggestions": Suggestions
    }

    docx_file_path = export_to_docx(models)
    xlsx_file_path = export_to_xlsx(models)
    
    docx_file_path = export_to_docx(models)
    await message.answer_document(
        BufferedInputFile.from_file(docx_file_path, filename="database_export.docx"),
        caption="Данные в формате DOCX"
    )

    await message.answer_document(
        BufferedInputFile.from_file(xlsx_file_path, filename="database_export.xlsx"),
        caption="Данные в формате XLSX"
    )

    os.remove(docx_file_path)
    os.remove(xlsx_file_path)

@router.message(F.text == 'Создать резервную копию')
async def upload_backup(message: Message):
    await create_backup()
    await message.answer("Резервная копия создана успешно")

@router.message(F.text == 'Добавить книгу в БД')
async def add_book_through_tg(message: Message):
    user = UserInfo.get(tg_id=message.from_user.id)
    if user.role != 'admin':
        await message.answer('У вас нет прав для выполнения этой команды')
        return

    await message.answer('Отправьте данные о книге ответом на это сообщение в формате:\n'
                         'Название | Описание | Автор | Год | Жанр | Ссылка на скачивание\nПример:\n'
                         'Война и мир | Описание | Лев Толстой | 1869 год. | Роман | https://qwerty.com')
    
@router.message()
async def search_book(message: Message):
    if (message.reply_to_message and 
        'отправьте название книги ответом на это сообщение' in message.reply_to_message.text.lower()):
        Suggestions.create(
        user_id=UserInfo.get(tg_id=message.from_user.id),
        suggestion_text=message.text.strip(),
        )
        await message.answer(
        'Спасибо за ваше предложение! 📕\n'
        'Мы обязательно рассмотрим его и добавим книгу, если это возможно')
    elif (message.reply_to_message and 
        'отправьте данные о книге ответом на это сообщение в формате:' in message.reply_to_message.text.lower()):
        user = UserInfo.get(tg_id=message.from_user.id)
        if user.role != 'admin':
            return
        
        parts = [part.strip() for part in message.text.split('|')]
        if len(parts) != 6:
            await message.answer('Неверный формат данных. Убедитесь, что вы указали все 6 параметров')
            return
        
        name, description, author, year, genre, download_link = parts
        Book.create(name=name, description=description, author=author, year=year, genre=genre, download_link=download_link)
        
        await message.answer('Книга была успешно добавлена в базу данных')
    
    else:
        query = message.text.strip()

        books = Book.select().where(fn.LOWER(Book.name).contains(query.lower()))

        if not books:
            await message.answer('К сожалению, я ничего не нашёл по вашему запросу. '
                                 'Перепроверьте название книги или предложите её')

        buttons = []
        if len(books) > 1:
            for book in books:
                button = InlineKeyboardButton(
                    text=book.name,
                    callback_data=f"select_book:{book.id}"
                )
                buttons.append([button])
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await message.answer('Я нашёл несколько книг по вашему запросу. Выберите нужную из списка:',
                                 reply_markup=keyboard)
        else:
            book = books[0]
            await send_book_info(message, book)

@router.callback_query()
async def select_book(callback_query: CallbackQuery):
    if callback_query.data.startswith("select_book:"):
        book_id = int(callback_query.data.split(":")[1])
        book = Book.get(id=book_id)
        await send_book_info(callback_query.message, book)
        await callback_query.answer()
    
    elif callback_query.data.startswith("delete_suggestion:"):
        suggestion_id = int(callback_query.data.split(":")[1])
        suggestion = Suggestions.get(id=suggestion_id)
        suggestion.delete_instance()
        await callback_query.message.answer(f"Предложение {suggestion_id} было успешно удалено \n")
        await callback_query.answer()