import configparser                      # импорт модулей
import json
import os
import requests
from pprint import pprint
from tqdm import tqdm

config = configparser.ConfigParser()                # блок чтения входных данных из ini файла
config.read('sitings.ini')
user_name = config['data_key']['username']
name_folder = config['data_key']['name_folder']
token_vk = config['data_key']['token_vk']
token_Yan = config['data_key']['token_Yandex']

class VkApi:
    base_url_api = 'https://api.vk.com/method'                  # заводим постоянные атрибуты класса
    url_base_vk = 'https://cloud-api.yandex.net'
    def __init__(self, user_id, token, token_Yan, counts=5):      # определяем конструктор с переменными
        self.user_id = user_id
        self.token = token
        self.token_Yan = token_Yan
        self.counts = counts
        self.headers_dict = {'Authorization': f"OAuth {self.token_Yan}"}

    def get_params(self):       # определяем параметры API VK
        params = {
        'access_token': self.token,
        'owner_id': self.user_id,
        'album_id': 'wall',
        'photo_sizes': '1',
        'v': '5.199',
        'extended': '1'
        }
        return params

    def get_photos(self):                                   # получаем массив данных с VK
        response = requests.get(f'{self.base_url_api}/photos.get', params=self.get_params())
        base_list = response.json()
        if 'response' in base_list:
            print("Данные с VK получены успешно")          # лог проверки получения данных по первому ключу заголовка
        else:                                              # т.к. в случае некорректного токена ответ все равно '200'
            print('Ошибка токена. Доступ к данным с VK ограничен')
        return base_list

    def save_file(self,url_load, name_f):                # функция записи файлов в ЯД
        url_get_link = f'{self.url_base_vk}/v1/disk/resources/upload'
        params_file = {'path': f'{self.name_folder}/{name_f}.jpg'}
                                           # данные для запроса ссылки для записи в ЯД (имя папки, имя файла)
        response = requests.get(url_get_link, params=params_file, headers=self.headers_dict) # запрос ссылки в ЯД
        url_for_upload = response.json().get('href')      # получаем ссылку на запись из ответа ЯД
        response_f = requests.get(url_load)               # получаем файл с VK
        file = response_f.content                        # получаем байтовый контент данных
        requests.put(url_for_upload, file)              # запись файла в ЯД

    def create_folder(self, name_folder):              # создаем папку на ЯД
        self.name_folder = name_folder
        url_create_folder = f'{self.url_base_vk}/v1/disk/resources'
        params_folder = {'path': self.name_folder}
        requests.put(url_create_folder, params=params_folder, headers=self.headers_dict)
        print('создана папка на Ядиске')

    def save_files_YD(self):                  # функция записи
        result = []                            # определяем локальные переменные
        likes_list = []
        quantity = 1
        data = self.get_photos()
        for item in tqdm(data['response']['items']):
            if quantity <= self.counts:                     # определяем кол-во файлов в запись (5 по умолчанию)
                size = item['sizes'][-5]['type']
                photo_url = item['sizes'][-5]['url']
                if item['likes']['count'] in likes_list:
                    name = f"{item['likes']['count']}_{item['date']}"    # корректируем имя файла при совпадении
                else:
                    name = item['likes']['count']
                    likes_list += [name]
                self.save_file(photo_url, name)                     # записывам файл через ф-цию save_file
                # print(f'Загружено {quantity} фото')                  # лог загрузки файлов на Ядиск
                quantity += 1
                result += [{'file_name': f'{name}.jpg', 'size': size}]
        with open('result.json', 'w') as f:                              # запись json файла
            json.dump(result, f)
        print("Записан файл с результатами 'result.json'")                # лог записи файла json

user = VkApi(user_name, token_vk, token_Yan)
user.create_folder(name_folder)
user.save_files_YD()
