from pickle import TRUE
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#import pymysql
#import secrets

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://favbooks:favbooks@localhost/favbooks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db = SQLAlchemy(app)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/signUp')
def signUp():
    return 'Sign Up Page'

@app.route('/login')
def login():
    return 'Login Page'

@app.route('/home')
def home():
    return 'Home Page'
    



class User(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

    def __init__(self, fullname, email, password):
        self.fullname = fullname
        self.email = email
        self.password = password

if __name__ == '__main__':
        app.run(debug='TRUE')
        app.run(host = '0.0.0.0', port = 5000)
