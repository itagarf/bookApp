from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
#import pymysql
#import secrets

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://favbooks:favbooks@localhost/favbooks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SECRET_KEY'] = '!"£$%^&*()LKJHGFDSA}:@<>?' 

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def registered():
    session['secret']='sec'
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() 
    if user:
        flash('Email address already exists in the database!')
        return redirect(url_for('register'))

    new_user = User(email=email, fullname=fullname, password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def loggedIn():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))

    login_user(user, remember=remember)
    return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html', fullname= current_user.fullname)


@app.route('/premium')
def premium():
    return 'Premium Page'
    



class User(UserMixin, db.Model):
    id= db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))

    def __init__(self, fullname, email, password):
        self.fullname = fullname
        self.email = email
        self.password = password

if __name__ == '__main__':
        app.run(debug='TRUE')
        app.run(host = '0.0.0.0', port = 5000)
