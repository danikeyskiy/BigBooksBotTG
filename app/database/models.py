import datetime
import os
from peewee import *
from dotenv import load_dotenv


load_dotenv()
pg_db = PostgresqlDatabase(database=os.getenv('DATABASE'), user=os.getenv('USER'), password=os.getenv('PASSWORD'),
                           host=os.getenv('HOST'), port=os.getenv('PORT'))

class BaseModel(Model):
    class Meta:
        database = pg_db

class UserInfo(BaseModel):
    id = BigAutoField(primary_key=True)
    tg_id = BigIntegerField(unique=True)
    username = CharField(max_length=255, null=True)
    role = CharField(max_length=100)
    
class Book(BaseModel):
    id = BigAutoField(primary_key=True)
    name = CharField(max_length=255)
    description = TextField(null=True)
    author = CharField(max_length=100, null=True)
    year = CharField(max_length=100, null=True)
    genre = CharField(max_length=255, null=True)
    download_link = CharField(max_length=255)
    
class Downloads(BaseModel):
    id = BigAutoField(primary_key=True)
    user_id = ForeignKeyField(UserInfo, backref='downloads', on_delete='RESTRICT')
    book_id = ForeignKeyField(Book, backref='downloads', on_delete='RESTRICT')
    book_name = CharField(max_length=255)
    download_time = DateTimeField(default=datetime.datetime.now)
    
class Suggestions(BaseModel):
    id = BigAutoField(primary_key=True)
    user_id = ForeignKeyField(UserInfo, backref='suggestions', on_delete='RESTRICT')
    suggestion_text = CharField(max_length=255)
    suggestion_date = DateTimeField(default=datetime.datetime.now)