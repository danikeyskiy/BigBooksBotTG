# auto-generated snapshot
from peewee import *
import datetime
import peewee


snapshot = Snapshot()


@snapshot.append
class Book(peewee.Model):
    id = BigAutoField(primary_key=True)
    name = CharField(max_length=255)
    description = TextField(null=True)
    author = CharField(max_length=100, null=True)
    year = CharField(max_length=100, null=True)
    genre = CharField(max_length=255, null=True)
    download_link = CharField(max_length=255)
    class Meta:
        table_name = "book"


@snapshot.append
class UserInfo(peewee.Model):
    id = BigAutoField(primary_key=True)
    tg_id = BigIntegerField(unique=True)
    username = CharField(max_length=255, null=True)
    role = CharField(max_length=100)
    class Meta:
        table_name = "userinfo"


@snapshot.append
class Downloads(peewee.Model):
    id = BigAutoField(primary_key=True)
    user_id = snapshot.ForeignKeyField(backref='downloads', index=True, model='userinfo', on_delete='RESTRICT')
    book_id = snapshot.ForeignKeyField(backref='downloads', index=True, model='book', on_delete='RESTRICT')
    book_name = CharField(max_length=255)
    download_time = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = "downloads"


@snapshot.append
class Suggestions(peewee.Model):
    id = BigAutoField(primary_key=True)
    user_id = snapshot.ForeignKeyField(backref='suggestions', index=True, model='userinfo', on_delete='RESTRICT')
    suggestion_text = CharField(max_length=255)
    suggestion_date = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = "suggestions"


