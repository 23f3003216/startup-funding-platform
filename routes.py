from flask import Flask,render_template,request,flash,redirect,url_for

from werkzeug.security import generate_password_hash,check_password_hash

from app import app,db

from models import User,AdRequest,Campaign,Profile
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/login',methods={'POST'})
def login_post():
    username=request.form.get('username')
    password=request.form.get('password')
    if not username or not password:
        flash('Please fill all the details.')
        return redirect(url_for('login'))
    user=User.query.filter_by(username=username).first()
    if not user:
        flash('Username does not exist.')
        return redirect(url_for('login'))
    if not check_password_hash(user.passhash,password):
        flash('Password is incorrect')
        return redirect(url_for('login'))
    return redirect(url_for('index'))



@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/register',methods={'POST'})
def register_post():
    username=request.form.get('username')
    password=request.form.get('password')
    confirm_password=request.form.get('confirm_password')
    name=request.form.get('name')
    user_type=request.form.get('user_type')
    if not username or not password or not confirm_password or not user_type:
        flash('Please fill out all the details.')
        return redirect(url_for('register'))
    if password!=confirm_password:
        flash('Passwords do not match.')
        return redirect(url_for('register'))
    user=User.query.filter_by(username=username).first()
    if user:
        flash('Username is already taken.')
        return redirect(url_for('register'))
    password_hash=generate_password_hash(password)

    new_user=User(username=username,passhash=password_hash,name=name,user_type=user_type)
    db.session.add(new_user)
    db.session.commit()
    return redirect (url_for('login'))

    
    