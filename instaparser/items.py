# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    # имя страницы, подписки и подсписчиков которой парсим
    user_parser_name = scrapy.Field()
    # данные подписок и подписчиков
    user_id = scrapy.Field()
    username = scrapy.Field()
    photo = scrapy.Field()
    user_type = scrapy.Field()
    _id = scrapy.Field()

