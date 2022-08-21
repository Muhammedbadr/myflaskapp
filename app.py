from crypt import methods
from distutils.command.config import config
import email
from unicodedata import name
from unittest import result
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


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
        username = request.form{'username'}
        password_candidate=request.form['password']
        cur=mysql.connection.cursor()
        result=cur.execute("SELECT * FROM users WHERE username=%s",[username])
        if result > 0:
            data = 
    return render_template('login.html')



if __name__=='__main__':
    app.secret_key="secrt123"
    app.run(debug=True )


