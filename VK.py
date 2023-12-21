import configparser
import json
#import urllib.request
import os
import requests
#from urllib.parse import urlencode
from pprint import pprint

config = configparser.ConfigParser()
config.read('sitings.ini')
User_name = config['data_key']['username']
token_vk = config['data_key']['token_vk']
token_Yan = config['data_key']['token_Yandex']

class VK_API:
    BASE_URL_API = 'https://api.vk.com/method'
    def __init__(self, user_id, token, token_Yan, count_=5):
        self.user_id = user_id
        self.token = token
        self.token_Yan = token_Yan
        self.headers_dict = {'Authorization': f"OAuth {self.token_Yan}"}
        self.url_base_vk = 'https://cloud-api.yandex.net'

    def get_params(self):
        params = {
        'access_token': self.token,
         'owner_id': self.user_id,
         'album_id': 'wall',
        'photo_sizes': '1',
        'v': '5.199',
            'extended': '1'
        }
        return params

    def get_photos(self):
        response = requests.get(f'{self.BASE_URL_API}/photos.get', params=self.get_params())
        if 'response' in list(response.json().keys()):
            print("Данные с VK получены успешно")
        else:
            print('Ошибка токена. Доступ к данным с VK ограничен')
        return response.json()

    def save_file(self,url_load, name_f):
        url_get_link = f'{self.url_base_vk}/v1/disk/resources/upload'
        params_file = {'path': f'photos_VK/{name_f}.jpg'}
        response = requests.get(url_get_link, params=params_file, headers=self.headers_dict)
        url_for_upload = response.json().get('href')
        response_f = requests.get(url_load)
        file = response_f.content
        requests.put(url_for_upload, file)

    def save_files_YD(self):
        url_create_folder = f'{self.url_base_vk}/v1/disk/resources'
        params_folder = {'path': 'photos_VK'}
        requests.put(url_create_folder, params=params_folder, headers=self.headers_dict)
        result = []
        likes_ = []
        data = self.get_photos()
        for item in data['response']['items']:
           for el in item['sizes']:
               if el['type'] == 'z':
                   if item['likes']['count'] in likes_:
                       name = f"{item['likes']['count']}_{item['date']}"
                   else:
                       name = item['likes']['count']
                       likes_ += [name]
                   self.save_file(el['url'],name)
                   result += [{'file_name': f'{name}.jpg','size':el['type']}]
        with open('result.json', 'w') as f:
            json.dump(result, f)

USER_1 = VK_API(User_name, token_vk, token_Yan)
USER_1.save_files_YD()
