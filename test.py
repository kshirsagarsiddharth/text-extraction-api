from requests.api import request
from extraction import Preprocessing 
import os 
from tqdm import tqdm
BASE_PATH = '/mnt/d/rest_apis_python/text_analyzer_api/code/images_dir'
text = []
import json 
for image in tqdm(os.listdir('images_dir')):
    path = os.path.join(BASE_PATH, image)
    image_object = Preprocessing(path)
    image_object.correct_orientation()
    image_object.get_grayscale()
    image_object.thresholding()
    image_object.opening()
    json_item = {'path': str(image), 'text': image_object.extract_text()}
    text.append(json_item)
    


import json
with open('extracted_data.json', 'w', encoding='utf-8') as f:
    json.dump({'data':text}, f, ensure_ascii=False, indent=4)



print('done!!')


from app import User,db 
db.create_all() 
