import requests 
import os 
def create_user(username,password, url = 'http://127.0.0.1:5000/auth'):
    json_payload = {'username':username,'password': password}
    response = requests.post(url,json=json_payload)
    return response.text 

#create_user('siddharth5','siddharth')
# create_user('siddharth1','siddharth')
# create_user('siddharth2','siddharth')
# create_user('siddharth3','siddharth')

def get_jwt_token(username, password,url = 'http://127.0.0.1:5000/auth'): 
    json_payload = {'username':username,'password': password}
    response = requests.get(url, json=json_payload)
    return response


def upload_file(file_path,username,store_jwt_token,url = 'http://127.0.0.1:5000/image-upload'): 
    import base64
    import json   
    with open(file_path,'rb') as f: 
        im_byte = f.read() 
    img_b64 = base64.b64encode(im_byte).decode('utf-8') 
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'text/plain',
        'x-access-token': store_jwt_token.json()
        }
    payload = json.dumps({'image':img_b64, 
                          "image-name": os.path.basename(file_path),
                          "username": str(username)
                          }) 
    response = requests.post(url, data=payload, headers=headers)
    try:
        
        data = response.json()
        return data  
    except Exception as e:
       return response.text 




def extract_text(store_jwt_token, url = 'http://127.0.0.1:5000/text-extraction'):
    headers = {
        'x-access-token': store_jwt_token.json()
        }
    response = requests.get(url, headers=headers)
    try:
        
        data = response.json()
         
    except Exception as e:
        print(e)
        data = response.text  
       
    finally:
        return data 

# import os 
# store_jwt_token = get_jwt_token('siddharth','siddharth') 
# for image in os.listdir('images_dir')[:2]:
#     path = os.path.join('images_dir',image)
#     upload_file(path,'siddharth', store_jwt_token=store_jwt_token)

# import os 
# store_jwt_token = get_jwt_token('siddharth3','siddhardth') 
# for image in os.listdir('images_dir')[14:16]:
#     path = os.path.join('images_dir',image)
#     print(upload_file(path,'siddharth1', store_jwt_token=store_jwt_token))

store_jwt_token = get_jwt_token('siddharth','siddharth') 
print(extract_text(store_jwt_token))
