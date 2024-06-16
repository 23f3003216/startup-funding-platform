from flask import Flask,render_template,request,flash,redirect,url_for,session

from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from app import app,db

from models import User,AdRequest,Campaign,Profile

def auth_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' in session:
            return func(*args,**kwargs)
        else:
           flash('Kindly login first.')
           return redirect(url_for('login'))
    return inner


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login',methods=['POST'])
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
    
    session['user_id']=user.id
    flash('Login Successfully done')
    return redirect(url_for('index'))



@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register',methods=['POST'])
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




@app.route('/')
def index():
        return redirect(url_for('login'))


@app.route('/profile',methods=['GET','POST'])
def profile():
    if request.method=='GET':

     if 'user_id' in session:
       user_id=session['user_id']
       user=User.query.get(user_id)
       if not user:
           flash('User not found. Please log in again.')
           return redirect(url_for('login'))
       return render_template('profile.html', user=user)
     else:
        flash('Kindly login first.')
        return redirect(url_for('login'))
    
    elif request.method=='POST':
        username=request.form.get('username')
        cpassword=request.form.get('cpassword')
        password=request.form.get('password')
        name=request.form.get('name')

        if not username or not cpassword or not password:
            flash('Please fill all the details')
            return redirect(url_for('profile'))
        user=User.query.get(session['user_id'])
        if not check_password_hash(user.passhash,cpassword):
            flash('Incorrect password')
            return redirect(url_for('profile'))
        if username!=user.username:
            new_username=User.query.filter_by(username=username).first()
            if new_username:
                flash('Username already exists.')
                return redirect(url_for('profile'))
        new_password_hash=generate_password_hash(password)
        user.username=username
        user.passhash=new_password_hash
        user.name=name
        db.session.commit()
        flash('Profile Successfully Updated.')
        return redirect(url_for('profile'))

    

    
@app.route('/logout')
@auth_required
def logout():
    session.pop('user_id')
    flash('Successfully Logged Out')
    return redirect(url_for('login'))
  

    
    