from asyncio.log import logger
from datetime import date
import email
from distutils.command.config import config
import errno
from functools import wraps
from unicodedata import name
from unittest import result

from flask import (Flask, flash, logging, redirect, render_template, request,
                   session, url_for)
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from wtforms import Form, PasswordField, StringField, TextAreaField, validators

from data import Articles
app = Flask(__name__)
Articles=Articles()
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='6685'
app.config['MYSQL_DB']='myflaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)


@app.route('/')
def index( ):
    return render_template ('home.html')

@app.route('/about')
def about ():
    return render_template('about.html')

@app.route('/articles')
def articles ():
    return render_template('articles.html',articles=Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id )

class RegisterForm (Form):
    name= StringField('Name',[validators.length(min=1,max=50)])
    username =StringField('username',{validators.Length(min=4,max=25)})
    email=StringField('Email',{validators.Length(min=6, max=50)})
    password =PasswordField('Password',{
        validators.DataRequired(),
        validators.EqualTo('confirm', message='PasswordS do not match')
    }) 
    confirm=PasswordField('Confirm Password')

@app.route('/register',methods={'GET','POST'})
def register ():
    form = RegisterForm(request.form)
    
    if request.method=='POST'and form.validate():
        name = form.name.data
        email=form.email.data
        username=form.username.data
        password =sha256_crypt.encrypt(str(form.password.data))

        cur =mysql.connection.cursor()
        cur.execute('INSERT INTO users (name,email,username,password)VALUES(%s,%s,%s,%s)',(name,email,username,password))
        mysql.connection.commit()
        cur.close()
        
        flash("you are now registered and can log in","success")

        redirect(url_for('index'))
        
        return render_template("register.html",form=form) 

    return render_template("register.html",form=form)



@app.route('/login',methods=['GET','POST'])
def login():
    
    
    if request.method=='POST':
        username = request.form['username']
        password_candidate=request.form['password']
        cur=mysql.connection.cursor()
        result=cur.execute("SELECT * FROM users WHERE username=%s",[username])
        
        
        if result > 0:
            data = cur.fetchone()
            password = data ['password']

            
            if sha256_crypt.verify(password_candidate,password):
                session['logged_in']=True
                session['username']=username

                flash('you are now logged in ','success')
                return redirect (url_for('dashboard'))
            
            else:

                error='Invalid login'
                return render_template('login.html',error=error)
            cur.close()


        else:
            error='Username not found'
            return render_template('login.html',error=error)
    
    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in'in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized,please login','danger')
            return redirect(url_for(login))
    return wrap



@app.route('/logout')
def logout():
    session.clear()
    flash('uou are now logged out','success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


if __name__=='__main__':
    app.secret_key="secrt123"
    app.run(debug=True )


