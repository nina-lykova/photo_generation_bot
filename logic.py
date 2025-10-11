import json
import time
import os
import requests
import base64
from config import YOUR_SECRET, YOUR_KEY


class FusionBrainAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline_id, images=1, width=200, height=200):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": prompt
            }
        }

        data = {
            'pipeline_id': (None, pipeline_id),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['result']['files']

            attempts -= 1
            time.sleep(delay)


def photo(base64_string, output_filename):
    header = ""
    if "," in base64_string:
            header, base64_data = base64_string.split(',', 1)
    else:
        base64_data = base64_string # Если префикса нет, считаем, что вся строка - данные

        # Декодируем base64
        image_data = base64.b64decode(base64_data)

        # Определяем расширение файла (если возможно) из header
    file_extension = ".jpg" # Расширение по умолчанию
    if "data:image/jpeg" in header:
        file_extension = ".jpg"
    elif "data:image/png" in header:
        file_extension = ".png"
    elif "data:image/gif" in header:
        file_extension = ".gif"

    output_filename = os.path.splitext(output_filename)[0] + file_extension 
    with open(output_filename, 'wb') as f:
        f.write(image_data)

    return photo

           
if __name__ == '__main__':
    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', YOUR_KEY, YOUR_SECRET)
    pipeline_id = api.get_pipeline()
    uuid = api.generate("butterfly", pipeline_id)
    files = api.check_generation(uuid)
    output_filename_base = f"generated_image_{uuid}"  # Базовое имя файла
    photo(files[0], output_filename_base)
    

