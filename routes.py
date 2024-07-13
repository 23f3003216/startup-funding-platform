from flask import Flask,render_template,request,flash,redirect,url_for,session,Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from app import app,db,login_manager
from datetime import date,datetime

from models import User,AdRequest,Campaign,Admin,Influencer,Sponsor,InfluencerDetails, update_user_types

stats_bp=Blueprint('stats',__name__)

@login_required
@stats_bp.route('/sponsor/stats')
def sponsor_stats():
    if not isinstance(current_user, Sponsor):
        return "Unauthorized", 403
    total_campaigns = db.session.query(db.func.count(Campaign.id)) \
        .join(AdRequest, AdRequest.campaign_id == Campaign.id) \
        .filter(AdRequest.influencer_id == current_user.id) \
        .scalar()

    active_campaigns = db.session.query(db.func.count(Campaign.id)) \
        .join(AdRequest, AdRequest.campaign_id == Campaign.id) \
        .filter(AdRequest.influencer_id == current_user.id, Campaign.status == 'active') \
        .scalar()

    completed_campaigns = db.session.query(db.func.count(Campaign.id)) \
        .join(AdRequest, AdRequest.campaign_id == Campaign.id) \
        .filter(AdRequest.influencer_id == current_user.id, Campaign.status == 'completed') \
        .scalar()

    sponsor_stats = {
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'completed_campaigns': completed_campaigns
    }
    return render_template('sponsor_stats.html',stats=sponsor_stats)

@stats_bp.route('/influencer/stats')

def influencer_stats():
     if not isinstance(current_user, Influencer):
        return "Unauthorized", 403
     total_campaigns = db.session.query(db.func.count(Campaign.id)) \
        .join(AdRequest, AdRequest.campaign_id == Campaign.id) \
        .filter(AdRequest.influencer_id == current_user.id) \
        .scalar()

     active_campaigns = db.session.query(db.func.count(Campaign.id)) \
        .join(AdRequest, AdRequest.campaign_id == Campaign.id) \
        .filter(AdRequest.influencer_id == current_user.id, Campaign.status == 'active') \
        .scalar()

     completed_campaigns = db.session.query(db.func.count(Campaign.id)) \
        .join(AdRequest, AdRequest.campaign_id == Campaign.id) \
        .filter(AdRequest.influencer_id == current_user.id, Campaign.status == 'completed') \
        .scalar()

     influencer_stats = {
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'completed_campaigns': completed_campaigns}
     return render_template('influencer_stats.html',stats=influencer_stats)

def create_admin_user():
    admin=User.query.filter_by(user_type='admin').first()
    if not admin:
        password_hash = generate_password_hash('admin')  
        admin = Admin(username='admin', passhash=password_hash,user_type='admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully.") 
    else:
        print("Admin user already exists.") 

def setup():
    db.create_all()
    create_admin_user()
    update_user_types() 

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
    
    login_user(user)
    session['user_id']=user.id
    flash('Login Successfully done')
    if user.user_type=='admin':
        return redirect(url_for('admin_dashboard'))
    elif user.user_type=='sponsor':
        return redirect(url_for('sponsor_dashboard'))
    elif user.user_type=='influencer':
        return redirect(url_for('influencer_dashboard'))
    return redirect(url_for('index'))

if __name__== '__main__':
          setup()
          app.run(debug=True)





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
        niche = request.form['niche']
        reach = request.form.get('reach',0)
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


        new_influencer = Influencer(username=username, passhash=password_hash, name=name, platform=platform,niche=niche,reach=int(reach) if reach else None )
        db.session.add(new_influencer)
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


        new_sponsor = Sponsor(username=username, passhash=password_hash, name=name, industry=industry)
        db.session.add(new_sponsor)
        db.session.commit()
        flash('Registeration as a Sponsor completed Successfully.Please login now.')
        return redirect (url_for('login'))



@app.route('/')
@auth_required
def index():
        user_id=User.query.get(session['user_id'])
        if not user_id:
          flash('Kindly login first')
          return redirect(url_for('login'))
        try:
            user_id=int(user_id)
        except (ValueError,TypeError):
            flash('Invalid User ID in Session.')
            return redirect(url_for('login'))

        user=User.query.get(user_id)
        if not user:
            flash('User not found.Kindly login again.')
            return redirect(url_for('login'))


        if user.user_type=='admin':
            return redirect(url_for('admin_dashboard',user=user))
        elif user.user_type=='sponsor':
            return render_template('sponsor_dashboard',user=user)
        elif user.user_type=='influencer':
            return render_template('influencer_dashboard',user=user)

        return render_template('index.html',user=user)



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
@login_required
def logout():
    logout_user()
    session.pop('user_id',None)
    flash('Successfully Logged Out')
    return redirect(url_for('login'))
  
@app.route('/admin')
@auth_required
def admin_dashboard():
    total_users = User.query.count()
    total_sponsors = User.query.filter_by(user_type='sponsor').count()
    total_influencers = User.query.filter_by(user_type='influencer').count()
    total_campaigns = Campaign.query.count()
    total_public_campaigns = Campaign.query.filter_by(visibility='public').count()
    total_private_campaigns = Campaign.query.filter_by(visibility='private').count()
    total_ad_requests = AdRequest.query.count()
    total_pending_requests = AdRequest.query.filter_by(status='Pending').count()
    total_accepted_requests = AdRequest.query.filter_by(status='Accepted').count()
    total_rejected_requests = AdRequest.query.filter_by(status='Rejected').count()
    flagged_users = User.query.filter_by(flagged=True).count()
    flagged_campaigns = Campaign.query.filter_by(flagged=True).count()
    ongoing_campaigns_list = Campaign.query.filter(Campaign.end_date >= date.today()).all()
    flagged_users_list = User.query.filter_by(flagged=True).all()
    flagged_campaigns_list = Campaign.query.filter_by(flagged=True).all()
    flagged_items_list = flagged_users_list + flagged_campaigns_list

    return render_template('admin_dashboard.html', total_users=total_users, total_sponsors=total_sponsors,
                           total_influencers=total_influencers, total_campaigns=total_campaigns,
                           total_public_campaigns=total_public_campaigns, total_private_campaigns=total_private_campaigns,
                           total_ad_requests=total_ad_requests, total_pending_requests=total_pending_requests,
                           total_accepted_requests=total_accepted_requests, total_rejected_requests=total_rejected_requests,
                           flagged_users=flagged_users, flagged_campaigns=flagged_campaigns,
                           ongoing_campaigns=ongoing_campaigns_list, flagged_items=flagged_items_list)

@app.route('/admin/view_campaign/<int:campaign_id>')
@auth_required
def admin_view_campaign(campaign_id):
    campaign=Campaign.query.get_or_404(campaign_id)
    return render_template('admin_view_campaign.html',campaign=campaign)

@app.route('/admin/view_influencers')
@auth_required
def admin_view_influencers():
    influencers = User.query.filter(User.user_type == 'influencer', User.flagged.is_(False)).all()
    return render_template('admin_view_influencers.html',influencers=influencers)

@app.route('/admin/view_flagged_influencers')
@auth_required
def admin_view_flagged_influencers():
    flagged_influencers=User.query.filter(User.user_type=='influencer',User.flagged.is_(True)).all()
    return render_template('admin_view_flagged_influencers.html',flagged_influencers=flagged_influencers)

@app.route('/admin/flag_influencer/<int:influencer_id>')
@auth_required
def flag_influencer(influencer_id):
    influencer = User.query.get_or_404(influencer_id)
    influencer.flagged = True
    db.session.commit()
    flash('Influencer flagged.', 'success')
    return redirect(url_for('admin_view_influencers'))

@app.route('/admin/reinstate_influencer/<int:influencer_id>')
@auth_required
def reinstate_influencer(influencer_id):
    influencer = User.query.get_or_404(influencer_id)
    influencer.flagged = False
    db.session.commit()
    flash('Influencer reinstated.', 'success')
    return redirect(url_for('admin_view_flagged_influencers'))

@app.route('/admin/delete_influencer/<int:influencer_id>')
@auth_required
def delete_influencer(influencer_id):
    influencer = User.query.get_or_404(influencer_id)
    db.session.delete(influencer)
    db.session.commit()
    flash('Influencer deleted.', 'success')
    return redirect(url_for('admin_view_flagged_influencers'))


@app.route('/admin/view_item/<int:item_id>')
@auth_required
def view_item(item_id):
    user=User.query.filter_by(id=item_id,flagged=True).first()
    campaign=Campaign.query.filter_by(id=item_id,flagged=True).first()
    item=user or campaign
    if not item:
        flash('Item is not found','danger')
        return redirect(url_for('admin_dashboard'))
    return render_template('view_item.html',item=item)

@app.route('/admin/remove_item/<int:item_id>')
@auth_required
def remove_item(item_id):
    user=User.query.filter_by(id=item_id,flagged=True).first()
    campaign=Campaign.query.filter_by(id=item_id,flagged=True).first()
    item=user or campaign
    if not item:
        flash('Item is not found','danger')
        return redirect(url_for('admin_dashboard'))
    db.session.delete(item)
    db.session.commit()
    flash('Item has been removed','success')
    return render_template('view_item.html',item=item)



@app.route('/influencer/dashboard')
@auth_required
def influencer_dashboard():
    user_id=session.get('user_id')
    if not user_id:
        flash('Kindly login first')
        return redirect(url_for('login'))
    influencer=Influencer.query.get(user_id)
    if not influencer:
        flash('Not Found!','danger')
        return redirect(url_for('login'))
    if current_user.flagged:
        active_campaigns = []
        new_requests = []
        return render_template('influencer_dashboard.html', user=influencer, details=None, active_campaigns=active_campaigns, new_requests=new_requests)
    else:
      details=InfluencerDetails.query.filter_by(user_id=user_id).first()
      active_campaigns=Campaign.query.join(AdRequest).filter(AdRequest.influencer_id == user_id, AdRequest.status == 'Accepted').all()
      new_requests = AdRequest.query.filter_by(influencer_id=user_id, status='Pending').all()
      return render_template('influencer_dashboard.html',user=influencer,details=details,active_campaigns=active_campaigns,new_requests=new_requests)


@app.route('/influencer/find-campaigns', methods=['GET','POST'])
@auth_required
def find_campaigns():
    if current_user.flagged:
        flash('You have been flagged by the Admin. You can not find any campaigns.','danger')
        return redirect(url_for('influencer_dashboard'))
    if request.method=='POST':
        pass
    campaigns=Campaign.query.filter(Campaign.sponsor_id.isnot(None)).all()
    return render_template('find_campaigns.html',campaigns=campaigns)

@app.route('/influencer/view_campaign_details/<int:campaign_id>',methods=['GET','POST'])
@auth_required
def view_campaign_details(campaign_id):
          campaign=Campaign.query.get_or_404(campaign_id)
          ad_request=AdRequest.query.filter_by(campaign_id=campaign_id).first()
          if request.method=='POST':
                 ad_name=request.form.get('ad_name')
                 description=request.form.get('description')
                 terms=request.form.get('terms')
                 payment=request.form.get('payment')
                 influencer_id=request.form.get('influencer_id')
                 combined_description = f"Ad Name: {ad_name}\nDescription: {description}\nTerms: {terms}"
                 new_ad_request=AdRequest(requirements=combined_description,campaign_id=campaign_id,influencer_id=influencer_id,payment_amount=payment,status='Pending')
                 db.session.add(new_ad_request)
                 db.session.commit()
                 flash("Ad Request created successfully")
                 return redirect(url_for('influencer_dashboard'))

          return render_template('view_campaign_details.html',campaign=campaign,ad_request=ad_request)

@app.route('/mark_completed/<int:campaign_id>', methods=['POST'])
@login_required
def mark_completed(campaign_id):
    if not isinstance(current_user,Influencer):
        return "Unauthorized",403
    
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.completion_status = True
    db.session.commit()
    flash('Campaign marked as completed.', 'success')
    return redirect(url_for('influencer_dashboard'))





@app.route('/sponsor/dashboard')
@auth_required
def sponsor_dashboard():
    user_id=session.get('user_id')
    if not user_id:
        flash('Kindly login first')
        return redirect(url_for('login'))
    sponsor=Sponsor.query.get(user_id)
    if not sponsor:
        flash('Not Found!','danger')
        return redirect(url_for('login'))
    active_campaigns=Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    new_requests=AdRequest.query.join(Campaign).filter(Campaign.sponsor_id==sponsor.id,AdRequest.status=='Pending').all()
    return render_template('sponsor_dashboard.html',user=sponsor,active_campaigns=active_campaigns,new_requests=new_requests)


@app.route('/sponsor/create-campaign',methods=(['GET','POST']))
@auth_required
def create_campaign():
    if request.method=='POST':
        name=request.form.get('name')
        description=request.form.get('description')
        start_date_str=request.form.get('start_date')
        end_date_str=request.form.get('end_date')
        visibility = request.form.get('visibility')
        budget = float(request.form.get('budget'))
        sponsor_id=session.get('user_id')

        start_date=datetime.strptime(start_date_str,'%Y-%m-%d').date()
        end_date=datetime.strptime(end_date_str,'%Y-%m-%d').date()

        if visibility=='private':
            niche=request.form.get('niche')
            new_campaign=Campaign(name=name,description=description,start_date=start_date,
                              end_date=end_date,visibility =visibility , budget = budget ,sponsor_id=sponsor_id,niche=niche)
        else:
            new_campaign=Campaign(name=name,description=description,start_date=start_date,
                              end_date=end_date,visibility =visibility , budget = budget ,sponsor_id=sponsor_id)
            

        db.session.add(new_campaign)
        db.session.commit()
        flash("Campaign has been created","success")
        return redirect(url_for('sponsor_dashboard'))
    else:
        return render_template('new_campaign.html')


@app.route('/sponsor/delete-campaign/<int:campaign_id>', methods=['GET','POST'])
@auth_required
def delete_campaign(campaign_id):
    campaign=Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash("Campaign has been deleted","success")
    return redirect(url_for('sponsor_dashboard'))

@app.route('/sponsor/create_ad_request/<int:campaign_id>/<int:influencer_id>', methods=['GET', 'POST'])
@auth_required
def create_ad_request(campaign_id, influencer_id):
    if influencer.flagged:
        flash('You cannot create ad requests for this influencer because they are flagged.', 'danger')
        return redirect(url_for('find_influencers'))
    
    if request.method == 'POST':
        requirements = request.form.get('requirements')
        payment_amount = request.form.get('payment_amount')
        
        if not payment_amount:
            flash('Payment amount is required.')
            return redirect(url_for('create_ad_request', campaign_id=campaign_id, influencer_id=influencer_id))
        
        try:
            payment_amount = float(payment_amount)
        except ValueError:
            flash('Invalid payment amount.')
            return redirect(url_for('create_ad_request', campaign_id=campaign_id, influencer_id=influencer_id))
        
        status = 'Pending'
        new_ad_request = AdRequest(campaign_id=campaign_id, influencer_id=influencer_id, requirements=requirements, payment_amount=payment_amount, status=status)
        db.session.add(new_ad_request)
        db.session.commit()
        
        flash("Ad Request has been created", "success")
        return redirect(url_for('sponsor_dashboard'))
    campaign = Campaign.query.get_or_404(campaign_id)
    influencer = Influencer.query.get_or_404(influencer_id)
    return render_template('new_ad_request.html', campaign=campaign, influencer=influencer)
    
@app.route('/confirm_completion/<int:campaign_id>', methods=['POST'])
@login_required
def confirm_completion(campaign_id):
    if not isinstance(current_user,Sponsor):
        return "Unauthorized",403
    
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign:
        campaign.completion_status = True
        db.session.commit()
        flash('Campaign completion confirmed!', 'success')
    return redirect(url_for('sponsor_dashboard'))


@app.route('/sponsor/delete-ad-request/<int:request_id>')
@auth_required
def delete_ad_request(request_id):
    ad_request=AdRequest.query.get_or_404(request_id)
    db.session.delete(ad_request)
    db.session.commit()
    flash("Ad Request has been deleted","success")
    return redirect(url_for('sponsor_dashboard'))


@app.route('/sponsor/find-influencers',methods=['GET','POST'])
@auth_required
def find_influencers():
    influencers=[]
    if request.method=='POST':
        niche=request.form.get('niche')
        min_followers = request.form.get('min_followers', 0)
        campaign_id=1
        query=Influencer.query.filter(Influencer.flagged==False)
        if niche:
            query=query.filter(Influencer.niche.ilike(f"%{niche}%"))
        if min_followers:
            query.filter(Influencer.followers >= int(min_followers))
        
        influencers=query.all()    
        campaigns = Campaign.query.all() 
        return render_template('find_influencers.html',influencers=influencers,campaign_id=campaign_id,campaigns=campaigns)
    return render_template('find_influencers.html')



@app.route('/sponsor/view_influencer/<int:influencer_id>')
@auth_required
def view_influencer(influencer_id):
          influencer=Influencer.query.get_or_404(influencer_id)
          return render_template('view_influencer.html',influencer=influencer)

@app.route('/sponsor/view_campaign/<int:campaign_id>',methods=['GET','POST'])
@auth_required
def view_campaign(campaign_id):
          campaign=Campaign.query.get_or_404(campaign_id)
          ad_request=AdRequest.query.filter_by(campaign_id=campaign_id).first()
          if request.method=='POST':
                 ad_name=request.form.get('ad_name')
                 description=request.form.get('description')
                 terms=request.form.get('terms')
                 payment=request.form.get('payment')
                 influencer_id=request.form.get('influencer_id')
                 combined_description = f"Ad Name: {ad_name}\nDescription: {description}\nTerms: {terms}"
                 new_ad_request=AdRequest(requirements=combined_description,campaign_id=campaign_id,influencer_id=influencer_id,payment_amount=payment,status='Pending')
                 db.session.add(new_ad_request)
                 db.session.commit()
                 flash("Ad Request created successfully")
                 return redirect(url_for('sponsor_dashboard'))

          return render_template('view_campaign.html',campaign=campaign,ad_request=ad_request)



@app.route('/ad_request/<int:request_id>',methods=['GET','POST'])
@auth_required
def view_ad_request(request_id):
          ad_request=AdRequest.query.get_or_404(request_id)
          influencers=Influencer.query.all()
          if request.method=='POST':
              influencer_id=request.form.get('influencer_id')
              ad_request.influencer_id=influencer_id
              db.session.commit()
              flash('Influencer assigned successfully',"success")
              return redirect(url_for('sponsor_dashboard'))
          
          return render_template('view_ad_request.html',ad_request=ad_request,influencers=influencers)



@app.route('/request/<int:request_id>/view', methods=['GET'])
@login_required
def view_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)
    if ad_request.influencer_id != current_user.id:
        flash("Unauthorized action")
        return redirect(url_for('influencer_dashboard'))
    return render_template('view_request.html',request=ad_request)




@app.route('/request/<int:request_id>/accept', methods=['GET','POST'])
@login_required
def accept_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)
    if ad_request.influencer_id != current_user.id:
        flash("Unauthorized action")
        return redirect(url_for('influencer_dashboard'))
    if request.method=='POST':
        ad_request.status='Accepted'
        db.session.commit()
        flash("Ad Request Accepted")
        return redirect(url_for('influencer_dashboard'))
    return render_template('accept_request.html',request=ad_request)

   


@app.route('/request/<int:request_id>/reject', methods=['GET','POST'])
@login_required
def reject_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)
    if ad_request.influencer_id != current_user.id:
        flash("Unauthorized action")
        return redirect(url_for('influencer_dashboard'))
    if request.method=='POST':
        ad_request.status='Rejected'
        db.session.commit()
        flash("Ad Request Rejected")
        return redirect(url_for('influencer_dashboard'))
    return render_template('reject_request.html',request=ad_request)
    
@app.route('/completed_requests')
@login_required
def completed_requests():
    if not isinstance(current_user,Sponsor):
        return "Unauthorized", 403
    completed_campaigns=Campaign.query.filter_by(sponsor_id=current_user.id,status='Completed').all()
    return render_template('completed_requests.html', completed_campaigns= completed_campaigns)
    



@app.route('/make_payment/<int:campaign_id>', methods=['GET','POST'])
@login_required
def make_payment(campaign_id):
     if not isinstance(current_user,Sponsor):
        return "Unauthorized", 403
     if request.method=='POST':
        card_number=request.form['card_number']
        expiration_date=request.form['expiration_date']
        cvv=request.form['cvv']
        flash("Payment Successfully done",'sucess')
        return redirect(url_for('completed_requests'))
     campaign = Campaign.query.get_or_404(campaign_id)
     return render_template('make_payment.html',campaign=campaign)


password = 'admin'  
password_hash = generate_password_hash(password)
