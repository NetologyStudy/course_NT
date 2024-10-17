from pprint import pprint
import os
import json
from tqdm import tqdm
import logging
import requests
from settings import token_cfg


class Vk_Api:
    vk_url = 'https://api.vk.com/method/'

    def __init__(self, access_token, vk_version='5.131'):
        self.access_token = access_token
        self.vk_version = vk_version
        self.params = {'access_token': self.access_token, 'v': self.vk_version}

    def get_photo(self):
        params = {'owner_id': token_cfg.vkid,'album_id': 'profile', 'extended': 1, 'count': 5}
        response = requests.get(f'{self.vk_url}photos.get', params={**self.params, **params}).json()
        return response['response']['items']

    def save_photo(self):
        photos = self.get_photo()
        for photo in photos:
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

    def writing_to_json(self):
        with open('info.json', 'w', encoding='utf8') as f:
            photos = self.get_photo()
            info_photo = []
            for photo in photos:
                photo_size = photo['sizes']
                info_photo.append({'file_name': photo['likes']['count'],
                                   'size': photo_size[-1]['type']})
            json.dump(info_photo, f, indent=1)



class Yd_Api:

    def __init__(self, access_token):
        self.headers = {'Authorization': f'OAuth {access_token}'}
        self.params = {'path': 'Photos'}

    def create_folder(self):
        yd_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        response = requests.put(yd_url, headers=self.headers, params=self.params)

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
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    vk_id = Vk_Api(token_cfg.vktoken)
    vk_id.get_photo()
    vk_id.save_photo()
    yd_id = Yd_Api(token_cfg.ydtoken)
    yd_id.create_folder()
    yd_id.uploading_photos()




if __name__ == '__main__':
    main()
