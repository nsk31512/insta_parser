import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem



class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'velo5778'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1639660847:AbBQAHzi39W+qpFXjjmYzmPdvgOn56+ASnqKDkIpWGVeHDcc5OJO3hwrZw9g07G3Bssyh17MAwBl/45HTdsikS0Ddu8J7mnFuQm0ULAYapii/rxTT+T1vrvOEWC8uUAs94vri2KjC4C9jRoKtTLa'
    users_parse = ['natgeo', 'youreworldgram']

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'x-csrftoken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for self.user in self.users_parse:
                yield response.follow(
                    f'/{self.user}/',
                    callback=self.user_parsing,
                    cb_kwargs={'username': self.user}
            )

    def user_parsing(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'count': 12}
        link_parse = [
            f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?{urlencode(variables)}&search_surface=follow_list_page',
            f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?{urlencode(variables)}'
        ]

        cb_kwargs_dict = {'username': username, 'user_id': user_id, 'variables': deepcopy(variables)}
        mobile_user_agent = {'User-Agent': 'Instagram 155.0.0.37.107'}
        print()
        for link in link_parse:
            if 'followers' in link:
                yield response.follow(
                    link,
                    callback=self.followers_parse,
                    cb_kwargs=cb_kwargs_dict,
                    headers=mobile_user_agent
                )
            elif 'following' in link:
                yield response.follow(
                    link,
                    callback=self.following_parse,
                    cb_kwargs=cb_kwargs_dict,
                    headers=mobile_user_agent
                )

    def followers_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        if j_data.get('big_list'):
            variables['max_id'] = j_data.get('next_max_id')
            url_followers = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?{urlencode(variables)}&search_surface=follow_list_page'

            yield response.follow(
                url_followers,
                callback=self.followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                #имя страницы, подписки и подсписчиков которой парсим
                user_parser_name=username,
                #данные подписчика
                user_id=user.get('pk'),
                username=user.get('username'),
                photo=user.get('profile_pic_url'),
                user_type='follower'
            )
            yield item

    def following_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        if j_data.get('big_list'):
            variables['max_id'] = j_data.get('next_max_id')
            url_followers = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?{urlencode(variables)}'

            yield response.follow(
                url_followers,
                callback=self.following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                # имя страницы, подписки и подсписчиков которой парсим
                user_parser_name=username,
                # данные подписок
                user_id=user.get('pk'),
                username=user.get('username'),
                photo=user.get('profile_pic_url'),
                user_type='following'
            )
            yield item

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
