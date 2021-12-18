from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['instagram']
list_collections = db.list_collection_names()
input_user = input(f'БД содержит подписки и подписчиков следующих пользователей: {list_collections}.\n'
      f'Введите БД какого пользователя вы хотите посмотреть: ')
collection = db[input_user]
who_find = input('Информацию о каких пользователях хотите получить?'
                 'Для получения информации о подписчиках введите "followers"; '
                 'для получения информации о подписках введите "following":')

users = collection.find({'user_type': who_find})
for user in users:
    pprint(user)
