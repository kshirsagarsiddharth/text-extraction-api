import base64
import boto3
from flask import Flask, request, views

from flask_restful import Api, Resource, reqparse, abort 
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.security import generate_password_hash, check_password_hash 
import uuid
import jwt 
from functools import wraps 
import io
from PIL import Image as pil_image
from extraction import Preprocessing 
from tqdm import tqdm 
import numpy as np 

app = Flask(__name__) 
api = Api(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = '8hfdiDKLFHCVHNe495fhhducudf' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)  
    public_id = db.Column(db.Integer, unique = True) 
    name = db.Column(db.String(50), unique = True) 
    password = db.Column(db.String(80)) 
    admin = db.Column(db.Boolean) 
    #images = db.relationship('Images', backref = 'image', lazy = True)

class Images(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_s3_path = db.Column(db.String(100), nullable = False)


#'/user' {'username': <user_name>, 'password': <password>}
class UserResources(Resource):  
    parser = reqparse.RequestParser()  
    parser.add_argument(
        'username',
        type = str,
        required = True,
        help = 'Username cannot be blank'
        
    )

    parser.add_argument(
        'password',
        type = str,
        required = True,
        help = 'Password cannot be blank'
        
    )
    
    
    def post(self): 
        data = UserResources.parser.parse_args() 

        user_object = User.query.filter_by(name = data['username']).first()

        if user_object:
            return "The username is taken please choose another username!!"  
        hashed_password = generate_password_hash(data['password'], method = 'sha256') 
        new_user = User(public_id = str(uuid.uuid4()),
        name = data['username'],
        password = hashed_password,
        admin = False 
        )
        db.session.add(new_user)
        db.session.commit()

        return "New user created" 
    
    def get(self):
        auth = UserResources.parser.parse_args() 
        user_object = User.query.filter_by(name = auth['username']).first()
        #print(user_object.username)
        if not user_object:
            return "There is no user present with this name"
        
        if check_password_hash(user_object.password,auth.password):
            token = jwt.encode({'username': str(user_object.name)}, key = app.config['SECRET_KEY'], algorithm='HS256')
            return token 
        
        return "The password is incorrect please try again!!" 
    
    def delete(self):
        auth = UserResources.parser.parse_args() 
        user_object = User.query.filter_by(name = auth['username']).first()
        #print(user_object.username)
        if not user_object:
            return "There is no user present with this name"
        
        if check_password_hash(user_object.password,auth.password):
            db.session.delete(user_object) 
            db.session.commit()
            return "User deleted successfully"
        
        return "The password is incorrect please try again!!"

def decorator(request): 
        token = None 
        if 'x-access-token' in request.headers: 
            token = request.headers['x-access-token'] 
        if not token: 
            return None 
        try:
            # in this case we are getting the provided token which has public_id encoded into it 
            # and once we decode the token we are returned the public_id and we use this public_id to query the database 
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
            current_user = User.query.filter_by(name = data['username']).first()
        except:
            return None 

class ImageResource(Resource):

    def upload_s3(img_bytes,image_name):
        s = io.BytesIO(img_bytes)    
        s3 = boto3.client('s3') 
        response = s3.upload_fileobj(s, 'image-analysis-bucket48549839', image_name)
        return response 



    def post(self):

        if not request.json or 'image' not in request.json:
            abort(400)

        token = request.headers['x-access-token'] 
        if not token:
            return 'Missing Header'
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        if not data:
            return 'Invalid Token'

        current_user = User.query.filter_by(name = data['username']).first()

        image_name = request.json['image-name']
        if image_name[-3:] in ('jpg','png'):
            
            username = request.json['username']
            img_b64 = request.json['image']
            # get base 64 encoded string 
            img_bytes = base64.b64decode(img_b64.encode('utf-8')) 
            
            image_name = f"{username}-{uuid.uuid1()}-{image_name}"
            new_image = Images(user_id = current_user.id, image_s3_path = image_name)
            db.session.add(new_image)
            db.session.commit()
            response =  ImageResource.upload_s3(img_bytes,image_name)
        return 'Image added Succesfully!!'

class PerformExtraction(Resource):
    @staticmethod
    def download_s3_object(KEY):
        s3 = boto3.resource('s3') 
        BUCKET_NAME = 'image-analysis-bucket48549839'
        bucket = s3.Bucket(BUCKET_NAME)
        bucket_object = bucket.Object(KEY)
        response = bucket_object.get()
        unstreamed_image = pil_image.open(response['Body'])
        image_array = np.array(unstreamed_image)
        return image_array 
    
    @staticmethod
    def extract_text(image_array):
        image_object = Preprocessing(image_array)
        image_object.correct_orientation()
        image_object.get_grayscale()
        image_object.thresholding()
        image_object.opening()
        return image_object.extract_text()



    def get(self):
        token = request.headers['x-access-token'] 
        if not token:
            return 'Missing Header'
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        if not data:
            return 'Invalid Token'

        s3_images_list = []
        current_user = User.query.filter_by(name = data['username']).first()
        user_images = Images.query.filter_by(user_id = current_user.id).all()
        for this_path in user_images:
            s3_images_list.append(this_path.image_s3_path)
        file_object = open(str(current_user.id) +'-'+ current_user.name + '.txt', 'a+')
        for KEY in tqdm(s3_images_list):
            image_array = PerformExtraction.download_s3_object(KEY)
            extracted_text = PerformExtraction.extract_text(image_array)
            file_object.write(extracted_text)
        file_object.close()
            
        return "Successfully Extracted Text"

class AnayzeText: 
    pass 

api.add_resource(PerformExtraction,'/text-extraction')
api.add_resource(ImageResource,'/image-upload')
api.add_resource(UserResources,'/auth')



if __name__ == '__main__':
    # if we inport some stuff from app 
    # this below command might be executed 
    # to remedy this we use __name__ == '__main__'
    # i.e only if this file app.py is run we run the below code 
    # i.e the main file is run
    app.run(port = 5000, debug=True)