import configparser                      # импорт модулей
import json
import os
import requests
from pprint import pprint

config = configparser.ConfigParser()                # блок чтения входных данных из ini файла
config.read('sitings.ini')
User_name = config['data_key']['username']
token_vk = config['data_key']['token_vk']
token_Yan = config['data_key']['token_Yandex']

class VK_API:
    BASE_URL_API = 'https://api.vk.com/method'                  # заводим постоянные атрибуты класса
    url_base_vk = 'https://cloud-api.yandex.net'
    def __init__(self, user_id, token, token_Yan, count_=5):      # определяем конструктор с переменными
        self.user_id = user_id
        self.token = token
        self.token_Yan = token_Yan
        self.count = count_
        self.headers_dict = {'Authorization': f"OAuth {self.token_Yan}"}

    def get_params(self):       # определяем параметры API VK
        params = {
        'access_token': self.token,
         'owner_id': self.user_id,
         'album_id': 'profile',
        'photo_sizes': '1',
        'v': '5.199',
            'extended': '1'
        }
        return params

    def get_photos(self):                                   # получаем массив данных с VK
        response = requests.get(f'{self.BASE_URL_API}/photos.get', params=self.get_params())
        if 'response' in list(response.json().keys()):
            print("Данные с VK получены успешно")          # лог проверки получения данных по первому ключу заголовка
        else:                                              # т.к. в случае некорректного токена ответ все равно '200'
            print('Ошибка токена. Доступ к данным с VK ограничен')
        return response.json()
        # with open('data.json') as f:          # отладка по массиву из файла (для удобства)
        #     data = json.load(f)
        # return data

    def save_file(self,url_load, name_f):                # функция записи файлов в ЯД
        url_get_link = f'{self.url_base_vk}/v1/disk/resources/upload'
        params_file = {'path': f'photos_VK/{name_f}.jpg'}
        # данные для запроса ссылки для записи в ЯД (имя папки, имя файла)
        response = requests.get(url_get_link, params=params_file, headers=self.headers_dict) # запрос ссылки в ЯД
        url_for_upload = response.json().get('href')      # получаем ссылку на запись из ответа ЯД
        response_f = requests.get(url_load)               # получаем файл с VK
        file = response_f.content                        # получаем байтовый контент данных
        requests.put(url_for_upload, file)              # запись файла в ЯД

    def save_files_YD(self):                  # функция записи
        url_create_folder = f'{self.url_base_vk}/v1/disk/resources'
        params_folder = {'path': 'photos_VK'}
        requests.put(url_create_folder, params=params_folder, headers=self.headers_dict)  #создаем папку на ЯД
        print('создана папка на Ядиске')
        result = []                            # определяем локальные переменные
        likes_ = []
        count_ = 1
        data = self.get_photos()
        for item in data['response']['items']:
            if count_ <= self.count:             # определяем кол-во файлов в запись (5 по умолчанию)
                for el in item['sizes']:
                    if el['type'] == 'z':        # берем данные с максимальным размером фото
                        if item['likes']['count'] in likes_:
                            name = f"{item['likes']['count']}_{item['date']}"   #корректируем имя файла при совпадении
                        else:
                            name = item['likes']['count']
                            likes_ += [name]
                        self.save_file(el['url'],name)                   # записывам файл через ф-цию save_file
                        print(f'Загружено {count_} фото')                # лог загрузки файлов на Ядиск
                        count_ += 1
                        result += [{'file_name': f'{name}.jpg','size': el['type']}]
        with open('result.json', 'w') as f:                              # запись json файла
            json.dump(result, f)
        print("Записан файл с результатами 'result.json'")                # лог записи файла json

USER_1 = VK_API(User_name, token_vk, token_Yan)
USER_1.save_files_YD()                              # ПУСК )
