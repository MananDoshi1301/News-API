from flask import Flask
from app.database import init_db
from flask_jwt_extended import JWTManager

def create_app():
    server = Flask(__name__)
    server.config['MYSQL_HOST'] = 'localhost'
    server.config['MYSQL_USER'] = 'root'
    server.config['MYSQL_PASSWORD'] = 'your_new_password'
    server.config['MYSQL_DB'] = 'news_api'
    server.config['JWT_SECRET_KEY'] = 'bea07ed1f05ab86779ed3deadd8cb4032570b3806c46b410b77050f8e2b5654e'    
    jwt = JWTManager(server)        
    return server