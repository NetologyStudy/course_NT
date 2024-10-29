import os
import json
import time
from tqdm import tqdm
import logging
import requests
from settings import token_cfg


class VkApi:
    vk_url = 'https://api.vk.com/method/'

    def __init__(self, access_token, vk_version='5.131'):
        self.access_token = access_token
        self.vk_version = vk_version
        self.params = {'access_token': self.access_token, 'v': self.vk_version}

    def get_photo(self, vk_id=input('Введите свой ВК ID: ')):
        params = {'owner_id': vk_id, 'album_id': 'profile', 'extended': 1, 'count': 5}
        response = requests.get(f'{self.vk_url}photos.get', params={**self.params, **params}).json()
        return response['response']['items']


    def save_photo(self, photos):
        for photo in tqdm(photos, desc='Save photos'):
            time.sleep(0.5)
            file_name = photo['likes']['count']
            photo_url = photo['orig_photo']['url']
            try:
                photo_response = requests.get(photo_url)
                with open(f'Image/{file_name}.jpg', 'wb') as f:
                    f.write(photo_response.content)
                    logging.info(f'Фотография {file_name}.jpg успешно сохранена!')
            except requests.exceptions.RequestException as req_e:
                logging.error(f"Ошибка запроса при загрузке фото: {photo_url}, ошибка: {req_e}")
            except OSError as os_e:
                logging.error(f"Ошибка при сохранении фото: {file_name}.jpg, ошибка: {os_e}")
            except Exception as e:
                logging.error(f"Произошла непредвиденная ошибка при загрузке фото: {photo_url}, ошибка: {e}")


        logging.info(f'Фотографии успешно сохранены!')


    def writing_to_json(self, photos):
        with open('info.json', 'w', encoding='utf8') as f:
            info_photo = []
            for photo in photos:
                photo_size = photo['sizes']
                info_photo.append({'file_name': photo['likes']['count'],
                                   'size': photo_size[-1]['type']})
            json.dump(info_photo, f, indent=1)



class YdApi:
    def __init__(self, access_token):
        self.headers = {'Authorization': f'OAuth {access_token}'}


    def create_folder(self, name_folder):
        yd_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        response = requests.put(yd_url, headers=self.headers, params={'path': name_folder})


    def uploading_photos(self):

        directory = 'Image'

        if not os.path.exists(directory):
            raise FileNotFoundError(f"Директория {directory} не найдена")
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.jpg')]

        try:
            for filename in tqdm(files, desc='Uploading photos'):
                file_path = os.path.join(directory, filename)
                response = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                        params={'path': f'Photos/{filename}'},
                                        headers=self.headers).json()
                url_upload = response['href']
                with open(file_path, 'rb') as file:
                    requests.put(url_upload, files={'file': file})
                    logging.info(f'Фотография {filename} успешно загружена на Яндекс.Диск!')
        except requests.exceptions.RequestException as req_e:
            logging.error(f"Ошибка запроса: {req_e}")
        except FileNotFoundError as fnf_e:
            logging.error(f"Файл не найден: {fnf_e}")
        except ValueError as val_e:
            logging.error(f"Ошибка значения: {val_e}")
        except Exception as e:
            logging.error(f"Произошла непредвиденная ошибка: {e}")

        else:
            logging.info('Фотографии успешно загружены на Яндекс.Диск!')






def main():
    logging.basicConfig(
        level=logging.INFO,
        format=' %(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    v_k = VkApi(token_cfg.vktoken)
    photos = v_k.get_photo()
    v_k.save_photo(photos)
    v_k.writing_to_json(photos)
    time.sleep(0.5)
    yd_token = input('Введите свой токен Яндекс Диска: ')
    y_d = YdApi(yd_token)
    y_d.create_folder('Photos')
    y_d.uploading_photos()




if __name__ == '__main__':
    main()
