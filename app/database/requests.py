from app.database.models import *
from aiogram.types import Message

async def send_book_info(message: Message, book):
    book_info = (
        f"<b>Название:</b> {book.name}\n"
        f"<b>Описание:</b> {book.description}\n"
        f"<b>Автор:</b> {book.author}\n"
        f"<b>Год:</b> {book.year}\n"
        f"<b>Жанр:</b> {book.genre}\n"
        f"\n<a href=\"{book.download_link}\">Скачать</a>"
    )
    
    user = UserInfo.get(tg_id=message.chat.id)
    Downloads.create(
        user_id=user,
        book_id=book,
        book_name=book.name
    )
    
    await message.answer(book_info, parse_mode="HTML")