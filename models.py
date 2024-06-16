from app import app
from app import db
from sqlalchemy import String,Boolean,Enum,Integer,Column,ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(32),unique=True)
    passhash=db.Column(db.String(256),nullable=False)
    name=db.Column(db.String(64),nullable=True)
    user_type=db.Column(Enum('sponsor','influencer','admin'),nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def is_sponsor(self):
        return self.user_type=='sponsor'
    def is_influencer(self):
        return self.user_type=='influencer'

class Campaign(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(256),unique=False)
    description=db.Column(db.Text,nullable=True)
    start_date=db.Column(db.Date,nullable=False)
    end_date=db.Column(db.Date,nullable=False)
    budget=db.Column(db.Float,nullable=False)
    visibility=db.Column(Enum('public','private'),nullable=False,default='public')
    sponsor_id=db.Column(db.Integer,ForeignKey('user.id'),nullable=False)

    sponsor=relationship('User',backref='campaigns')

class AdRequest(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    campaign_id=db.Column(db.Integer,ForeignKey('campaign.id'),nullable=False)
    influencer_id=db.Column(db.Integer,ForeignKey('user.id'),nullable=False)
    requirements=db.Column(db.Text,nullable=True)
    payment_amount=db.Column(db.Float,nullable=False)
    status=db.Column(Enum('Pending','Accepted','rejected'),nullable=False,default='Pending')

    campaign=relationship('Campaign',backref='ad_requests')
    influencer=relationship('User',backref='ad_requests')

class Profile(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,ForeignKey('user.id'),nullable=False)
    name=db.Column(db.String(64),nullable=False)
    category=db.Column(db.String(64),nullable=False)
    niche=db.Column(db.String(64),nullable=False)
    reach=db.Column(db.Integer,nullable=False)
    
    user=relationship('User',backref='profile')
    with app.app_context():
        db.create_all()
        admin=User.query.filter_by(user_type='admin').first()
        if not admin:
            password_hash=generate_password_hash('admin')
            admin=User(username='admin',passhash=password_hash,name='Admin',user_type='admin',is_admin=True)
            db.session.add(admin)
            db.session.commit()





