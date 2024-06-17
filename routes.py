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



@app.route('/register/influencer',methods=(['GET','POST']))
def register_influencer():
    if request.method=='GET':
        return render_template('register_influencer.html')
    elif request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')
        name=request.form.get('name')
        platform=request.form.get('platform')
    if not username or not password or not confirm_password or not platform:
        flash('Please fill out all the details.')
        return redirect(url_for('register_influencer'))
    if password!=confirm_password:
        flash('Passwords do not match.')
        return redirect(url_for('register_influencer'))
    user=User.query.filter_by(username=username).first()
    if user:
        flash('Username is already taken.')
        return redirect(url_for('register_influencer'))
    password_hash=generate_password_hash(password)

    new_user=User(username=username,passhash=password_hash,name=name,platform=platform)
    profile=Profile(name=username,category='Influencer',niche='platform',reach=0,user=new_user)
    db.session.add(new_user)
    db.session.add(profile)
    db.session.commit()
    flash('Registeration as an Influencer completed Successfully.Please login now.')
    return redirect (url_for('login'))

@app.route('/register/sponsor',methods=['GET','POST'])
def register_sponsor():
    if request.method=='GET':
        return render_template('register_sponsor.html')
    elif request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')
        name=request.form.get('name')
        industry=request.form.get('industry')
    if not username or not password or not confirm_password or not industry:
        flash('Please fill out all the details.')
        return redirect(url_for('register_sponsor'))
    if password!=confirm_password:
        flash('Passwords do not match.')
        return redirect(url_for('register_sponsor'))
    user=User.query.filter_by(username=username).first()
    if user:
        flash('Username is already taken.')
        return redirect(url_for('register_sponsor'))
    password_hash=generate_password_hash(password)

    new_user=User(username=username,passhash=password_hash,name=name,industry=industry)
    profile=Profile(name=username,category='Sponsor',niche=industry,reach=0,user=new_user)
    db.session.add(new_user)
    db.session.add(profile)
    db.session.commit()
    flash('Registeration as a Sponsor completed Successfully.Please login now.')
    return redirect (url_for('login'))



@app.route('/')
@auth_required
def index():
        user=User.query.get(session['user_id'])
        if user.is_admin:
           return redirect (url_for('admin'))
        return render_template('index.html')



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
  
@app.route('/admin')
@auth_required
def admin():
    total_users=User.query.count()
    total_sponsors=User.query.filter_by(user_type='sponsor').count()
    total_influencers=User.query.filter_by(user_type='influencer').count()
    total_campaigns=Campaign.query.count()
    total_public_campaigns=Campaign.query.filter_by(visibility='public').count()
    total_private_campaigns=Campaign.query.filter_by(visibility='private').count()
    total_ad_requests=AdRequest.query.count()
    total_pending_requests=AdRequest.query.filter_by(status='Pending').count()
    total_accepted_requests=AdRequest.query.filter_by(status='Accepted').count()
    total_rejected_requests=AdRequest.query.filter_by(status='Rejected').count()
    flagged_users=User.query.filter_by(flagged=True).count()
    flagged_campaigns=Campaign.query.filter_by(flagged=True).count()

    return render_template('admin_dashboard.html',total_users=total_users, total_sponsors= total_sponsors,total_influencers=total_influencers,total_campaigns=total_campaigns,
                       total_public_campaigns=total_public_campaigns, total_private_campaigns=total_private_campaigns, total_ad_requests=total_ad_requests,
                           total_pending_requests=total_pending_requests,total_accepted_requests=total_accepted_requests,total_rejected_requests=total_rejected_requests,
                           flagged_users=flagged_users,flagged_campaigns=flagged_campaigns)


    
    