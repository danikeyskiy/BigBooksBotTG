from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Найти книгу')],
                                     [KeyboardButton(text='Предложить книгу')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')

admin = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Найти книгу')],
                                      [KeyboardButton(text='Посмотреть предложения пользователей'),
                                       KeyboardButton(text='Добавить книгу в БД')],
                                     [KeyboardButton(text='Выгрузить данные из БД'),
                                      KeyboardButton(text='Создать резервную копию')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')