
from flask import Flask, render_template, redirect, url_for, request, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_admin import Admin
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
#from flask_admin.contrib.sqla import ModelView
#import pymysql
#import secrets

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://favbooks:favbooks@localhost/favbooks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SECRET_KEY'] = '!"£$%^&*()LKJHGFDSA}:@<>?' 

app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51KVgyNKT9PivCmy0V7uroHKoYEzYEukCyP5mhIw4cFXfdJRZ2laFMlQ7rj16rR8EpbSyzGZAdqs3v9ivkJuhv85s00Y4HBxgck'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51KVgyNKT9PivCmy0cmIhCHEQq6S1E5I9o05AM4tUbEeHZSU1oCRaEt0keUaberqtnTmo7M2R1F9ENqY4SLtctdYp00yIrFwfNR'

db = SQLAlchemy(app)

admin = Admin(app, name='Admin Panel')

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
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    user = User.query.filter_by(email=email).first() 
    if user:
        flash('Email address already exists in the database!', category="error")
        return redirect(url_for('register'))
    
    if password1 != password2:
        flash('Both passwords do not match! Try registering again.', category='error')
        return redirect(url_for('register'))
    else:
        new_user = User(email=email, fullname=fullname, password=generate_password_hash(password1, method='sha256'), is_admin=False)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created. Please login with email and passsword', category='success')
        return redirect(url_for('login'))


@app.route('/admin_register')
def admin_register():
    return render_template('adminRegister.html')

@app.route('/admin_register', methods=['POST'])
def admin_registered():
    session['secret']='sec'
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    user = User.query.filter_by(email=email).first() 
    if user:
        flash('Email address already exists in the database!', category="error")
        return redirect(url_for('admin_register'))
    
    if password1 != password2:
        flash('Both passwords do not match! Try registering again.', category='error')
        return redirect(url_for('admin_register'))
    else:
        new_user = User(email=email, fullname=fullname, password=generate_password_hash(password1, method='sha256'), is_admin=True)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created. Please login with email and passsword', category='success')
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
        flash('Invalid email or password! Please check your login details and try again.', category='error')
        return redirect(url_for('login'))

    login_user(user, remember=remember)
    if current_user.is_admin == True:
        return redirect(url_for('adminHome'))
    else:
        return redirect(url_for('home'))

#A different method for login is:
#@login_manager.user_loader
#def load_user(id):
#    return User.quer.get(int(id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/home')
@login_required
def home():

    """ stripe.api_key = ''
    session = stripid """


    news = News.query.all()
    cBooks=ChildrenBooks.query.all()
    """ images=ChildrenBooks.query.all() """
    aBooks = AdultBooks.query.all()
    """ send_file(BytesIO(cBooks.image))
    return render_template('home.html', cBooks=cBooks) """
    """ base64Image = [base64.b64encode(ChildrenBooks).decode("utf-8") for images.image in images] """
    return render_template('home.html', cBooks=cBooks, aBooks=aBooks, news=news)
    
    """ , images=base64Image )"""

#https://www.reddit.com/r/flask/comments/mgu5tq/image_doesnt_display_properly_from_db/


@app.route('/admin-home')
@login_required
def adminHome():
    return render_template('adminHome.html', fullname= current_user.fullname)
    
#chldren books

@app.route('/add-children-book-details')
@login_required
def childrenBooks():
    return render_template('addChildrenBooks.html')

@app.route('/add-children-book-details', methods=['POST'])
@login_required
def addChilrenBooks():
    image = request.files['image']
    title = request.form['title']
    author = request.form['author']
    price = request.form['price']
    
    filename = secure_filename(image.filename)

    new_book = ChildrenBooks(image=image.read(), title=title, author=author, price=price, filename=filename)
    db.session.add(new_book)
    db.session.commit()
    flash('Book details added!', category='success')
    return redirect(url_for('childrenBooks'))
    #return "Added!"

@app.route('/update-children-books')
@login_required
def updateChildrenBooks():
    books=ChildrenBooks.query.all()
    return render_template('updateChildrenBooks.html', books=books)

@app.route('/edit-children-books/<int:bookId>', methods=['POST', 'GET'])
@login_required
def editChildrenBooks(bookId):
    book = ChildrenBooks.query.get(bookId)
    if request.method == 'POST':
        image = request.files['image']
        book.image = image.read()
        book.title = request.form['title']
        book.author = request.form['author']
        book.price = request.form['price']
        book.filename = secure_filename(image.filename)

        db.session.commit()
        flash('Details of book updated', category='success')
        return redirect('/update-children-books')
        
    else:
        return render_template('editChildrenBooks.html', book=book)


# teens and adult books


@app.route('/add-adult-book-details')
@login_required
def adultBooks():
    return render_template('addAdultBooks.html')

@app.route('/add-adult-book-details', methods=['POST'])
@login_required
def addAdultBooks():
    image = request.files['image']
    title = request.form['title']
    author = request.form['author']
    price = request.form['price']
    
    filename = secure_filename(image.filename)

    new_book = AdultBooks(image=image.read(), title=title, author=author, price=price, filename=filename)
    db.session.add(new_book)
    db.session.commit()
    flash('Book details added!', category='success')
    return redirect(url_for('adultBooks'))
    #return "Added!"

@app.route('/update-adult-books')
@login_required
def updateAdultBooks():
    books=AdultBooks.query.all()
    return render_template('updateAdultBooks.html', books=books)

@app.route('/edit-adult-books/<int:bookId>', methods=['POST', 'GET'])
@login_required
def editAdultBooks(bookId):
    book = AdultBooks.query.get(bookId)
    if request.method == 'POST':
        image = request.files['image']
        book.image = image.read()
        book.title = request.form['title']
        book.author = request.form['author']
        book.price = request.form['price']
        book.filename = secure_filename(image.filename)

        db.session.commit()
        flash('Details of book updated', category='success')
        return redirect('/update-adult-books')
        
    else:
        return render_template('editAdultBooks.html', book=book)


#add news


@app.route('/add-news')
@login_required
def news():
    return render_template('addNews.html')

@app.route('/add-news', methods=['POST'])
@login_required
def addNews():
    writeUp = request.form['writeUp']
    link = request.form['link']

    new_news = News(writeUp=writeUp, link=link)
    db.session.add(new_news)
    db.session.commit()
    flash('News details added!', category='success')
    return redirect(url_for('news'))


@app.route('/update-news')
@login_required
def updateNews():
    news=News.query.all()
    return render_template('updateNews.html', news=news)

@app.route('/edit-news/<int:newsId>', methods=['POST', 'GET'])
@login_required
def editNews(newsId):
    mainNews = News.query.get(newsId)
    if request.method == 'POST':
        mainNews.writeUp = request.form['writeUp']
        mainNews.link = request.form['link']

        db.session.commit()
        flash('News updated!', category='success')
        return redirect('/update-news')
        
    else:
        return render_template('editNews.html', mainNews=mainNews)




class User(UserMixin, db.Model):
    id= db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, fullname, email, password,is_admin):
        self.fullname = fullname
        self.email = email
        self.password = password
        self.is_admin = is_admin

class ChildrenBooks(db.Model):
    bookId = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary(length=(2**32)-1))
    title = db.Column(db.String(50), unique=True)
    author = db.Column(db.String(50))
    price = db.Column(db.DECIMAL(5,2))
    filename = db.Column(db.String(50))

    def __init__(self, image, title, author, price, filename):
        self.image = image
        self.title = title 
        self.author = author
        self.price = price
        self.filename = filename

class AdultBooks(db.Model):
    bookId = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary(length=(2**32)-1))
    title = db.Column(db.String(50), unique=True)
    author = db.Column(db.String(50))
    price = db.Column(db.DECIMAL(5,2))
    filename = db.Column(db.String(50))

    def __init__(self, image, title, author, price, filename):
        self.image = image
        self.title = title 
        self.author = author
        self.price = price
        self.filename = filename


class News(db.Model):
    newsId = db.Column(db.Integer, primary_key=True)
    writeUp = db.Column(db.String(255))
    link = db.Column(db.String(255))

    def __init__(self, writeUp, link):
        self.writeUp = writeUp
        self.link = link

""" class ChildBooks(db.Model):
    bookId = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary(length=(2**32)-1))
    title = db.Column(db.String(50), unique=True)
    filename = db.Column(db.String(50))

    def __init__(self, image, title, author, price, filename):
        self.image = image
        self.title = title 
        self.author = author
        self.price = price
        self.filename = filename
 """


if __name__ == '__main__':
        app.run(debug='TRUE')
        app.run(host = '0.0.0.0', port = 5000)
