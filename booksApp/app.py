import os
from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_admin import Admin
from werkzeug.utils import secure_filename
import stripe
import json
#from flaskext.mysql import MySQL

#db = MySQL()
 
# MySQL configurations

#from flask_admin.contrib.sqla import ModelView
#import pymysql
#import secrets

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app= Flask(__name__)
#DATABASE_URL = 'sqlite:///favbooks.db'
#app.config['DATABASE_URL'] = 'sqlite:///favbooks.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://favbooks:favbooks@localhost/favbooks'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://b559ce8186000f:59a32fce@us-cdbr-east-05.cleardb.net/heroku_69bcacc48fef29e'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
#app.config['SECRET_KEY'] = '!"£$%^&*()LKJHGFDSA}:@<>?' 
SECRET_KEY = '!"£$%^&*()LKJHGFDSrtyA}:@<>?' 

app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://jwoywkkybxxpzl:f9ff514bb7aa287644b3882bab2c59afe046082f73a33b9e6fdf73803de7ab0a@ec2-3-231-254-204.compute-1.amazonaws.com:5432/daq09ritmm2fo4'
app.config['SECRET_KEY'] = '!"£$%^&*()LKJHGFDSrtyA}:@<>?' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

#app.config['MYSQL_DATABASE_USER'] = 'b559ce8186000f'
#app.config['MYSQL_DATABASE_PASSWORD'] = '59a32fce'
#app.config['MYSQL_DATABASE_DB'] = 'heroku_69bcacc48fef29e'
#app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-east-05.cleardb.net'
#mysql.init_app(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51KVgyNKT9PivCmy0V7uroHKoYEzYEukCyP5mhIw4cFXfdJRZ2laFMlQ7rj16rR8EpbSyzGZAdqs3v9ivkJuhv85s00Y4HBxgck'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51KVgyNKT9PivCmy0cmIhCHEQq6S1E5I9o05AM4tUbEeHZSU1oCRaEt0keUaberqtnTmo7M2R1F9ENqY4SLtctdYp00yIrFwfNR'

stripe.api_key = app.config['STRIPE_SECRET_KEY']

db = SQLAlchemy(app)
#db.init_app(app)

admin = Admin(app, name='Admin Panel')

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



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
    news = News.query.all()
    cBooks=ChildrenBooks.query.all()
    aBooks = AdultBooks.query.all()
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('home.html', cBooks=cBooks, aBooks=aBooks, news=news, files=files)

@app.route('/children-book-payment')
def cPayment():

    session = stripe.checkout.Session.create(
        # success_url= 'https://example.com/success?session_id={checkout_session_id}',
        #cancel_url= 'https://example.com/cancel', 
        success_url= url_for('confirmation', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url= url_for('checkout', _external=True),
        line_items=[{
        'price': 'price_1KdzNJKT9PivCmy0IpCHd2vF',
        'quantity': 1,
        }],
        mode='payment',
    )

    sess = session['id']
    email = current_user.email
    new_session = UserSession(sessionId=sess,email=email)
    db.session.add(new_session)
    db.session.commit()
    return  {'checkout_session_id':session['id'], 
    'checkout_public_key':app.config['STRIPE_PUBLIC_KEY']}

@app.route('/teens-and-adult-book-payment')
def aPayment():

    session = stripe.checkout.Session.create(
        success_url= url_for('confirmation', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url= url_for('checkout', _external=True),
        line_items=[{
        'price': 'price_1KelkzKT9PivCmy0KWkwk0JH',
        'quantity': 1,
        }],
        mode='payment',
    )

    sess = session['id']
    email = current_user.email
    new_session = UserSession(sessionId=sess,email=email)
    db.session.add(new_session)
    db.session.commit()
    return  {'checkout_session_id':session['id'], 
    'checkout_public_key':app.config['STRIPE_PUBLIC_KEY']}


@app.route('/payment-confirmation')
@login_required
def confirmation():
    return render_template('confirmation.html', email= current_user.email)


endpoint_secret = 'whsec_07dc745262fed137ce699935fda038a5e43ae98a2f29bbdfa32145a6d5472780'
@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    #print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    #payload = request.get_data()
    #sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    #endpoint_secret = 'whsec_07dc745262fed137ce699935fda038a5e43ae98a2f29bbdfa32145a6d5472780'
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        #print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=4)
        
        
        sess_Id = session['id']
        description = line_items['data'][0]['description']
        amount_total = line_items['data'][0]['amount_total']
        quantity = line_items['data'][0]['quantity']

        new_invoice = Invoice(sessionId=sess_Id, description=description, amount_total=amount_total, quantity=quantity)
        db.session.add(new_invoice)
        db.session.commit()
    return jsonify(success=True)
   
    


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/invoice-details')
@login_required
def invoice():
    invoices=Invoice.query.all()
    return render_template('invoice.html', invoices=invoices)

@app.route('/payment-session-details')
@login_required
def paymentSession():
    pSessions=UserSession.query.all()
    return render_template('paymentSession.html', pSessions=pSessions)

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
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_book = ChildrenBooks(image=image.read(), title=title, author=author, price=price, filename=filename)
    db.session.add(new_book)
    db.session.commit()
    flash('Book details added!', category='success')
    return redirect(url_for('childrenBooks'))
    #return "Added!"

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


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
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_book = AdultBooks(image=image.read(), title=title, author=author, price=price, filename=filename)
    db.session.add(new_book)
    db.session.commit()
    flash('Book details added!', category='success')
    return redirect(url_for('adultBooks'))

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


#database tables

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


class Invoice(db.Model):
    invoiceId = db.Column(db.Integer, primary_key=True)
    sessionId = db.Column(db.String(100))
    description = db.Column(db.String(50))
    amount_total = db.Column(db.String(50))
    quantity = db.Column(db.String(50))

    def __init__(self,sessionId, description, amount_total, quantity):
        self.description = description
        self.sessionId = sessionId
        self.amount_total = amount_total
        self.quantity = quantity

class UserSession(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sessionId = db.Column(db.String(100))
    email = db.Column(db.String(50))

    def __init__(self, sessionId, email):
        self.sessionId = sessionId
        self.email = email


if __name__ == '__main__':
        #app.run(debug='TRUE')
        app.run(host = '0.0.0.0', port = 5000)
