# import base64
# import boto3
# from flask import Flask, request, views
# from flask_restful import Api, Resource, reqparse, abort 
# from flask_sqlalchemy import SQLAlchemy 
# from werkzeug.security import generate_password_hash, check_password_hash 
# import uuid
# import jwt 
# from functools import wraps 
# import io



# class UserResources(Resource):  
#     parser = reqparse.RequestParser()  
#     parser.add_argument(
#         'username',
#         type = str,
#         required = True,
#         help = 'Username cannot be blank'
        
#     )

#     parser.add_argument(
#         'password',
#         type = str,
#         required = True,
#         help = 'Password cannot be blank'
        
#     )
    
    
#     def post(self): 
#         data = UserResources.parser.parse_args() 

#         user_object = User.query.filter_by(name = data['username']).first()

#         if user_object:
#             return "The username is taken please choose another username!!"  
#         hashed_password = generate_password_hash(data['password'], method = 'sha256') 
#         new_user = User(public_id = str(uuid.uuid4()),
#         name = data['username'],
#         password = hashed_password,
#         admin = False 
#         )
#         db.session.add(new_user)
#         db.session.commit()

#         return "New user created" 
    
#     def get(self):
#         auth = UserResources.parser.parse_args() 
#         user_object = User.query.filter_by(name = auth['username']).first()
#         #print(user_object.username)
#         if not user_object:
#             return "There is no user present with this name"
        
#         if check_password_hash(user_object.password,auth.password):
#             token = jwt.encode({'username': str(user_object.name)}, key = app.config['SECRET_KEY'], algorithm='HS256')
#             return token 
        
#         return "The password is incorrect please try again!!" 
    
#     def delete(self):
#         auth = UserResources.parser.parse_args() 
#         user_object = User.query.filter_by(name = auth['username']).first()
#         #print(user_object.username)
#         if not user_object:
#             return "There is no user present with this name"
        
#         if check_password_hash(user_object.password,auth.password):
#             db.session.delete(user_object) 
#             db.session.commit()
#             return "User deleted successfully"
        
#         return "The password is incorrect please try again!!"

# def decorator(request): 
#         token = None 
#         if 'x-access-token' in request.headers: 
#             token = request.headers['x-access-token'] 
#         if not token: 
#             return None 
#         try:
#             # in this case we are getting the provided token which has public_id encoded into it 
#             # and once we decode the token we are returned the public_id and we use this public_id to query the database 
#             data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
#             current_user = User.query.filter_by(name = data['username']).first()
#         except:
#             return None 