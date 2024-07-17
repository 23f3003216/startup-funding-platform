from datetime import date,timedelta
import enum
from app import app,db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Boolean, Enum, Integer, Column, ForeignKey, Text, Date, Float
from sqlalchemy.orm import relationship,backref
from werkzeug.security import generate_password_hash
from flask_login import UserMixin


class User(db.Model,UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True)
    passhash = Column(String(256), nullable=False)
    name = Column(String(64), nullable=True)
    flagged = Column(Boolean, default=False)
    user_type = Column(String(50),nullable=False,default='user')
    influencer = db.relationship('Influencer', backref='user', uselist=False)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }
 
    def __init__(self, username, passhash, name=None):
        self.username = username
        self.passhash = passhash
        self.name = name
        self.user_type='user'

    def is_administrator(self):
        return False

class Admin(User):
    __tablename__ = 'admin'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    def __init__(self, username, passhash, name=None):
        super().__init__(username, passhash, name)
        self.username = username
        self.passhash = passhash
        self.name = name
        self.user_type='admin'

    def is_administrator(self):
        return True

class Sponsor(User):
    __tablename__ = 'sponsor'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    sponsor_type = Column(Enum('sponsor', name='sponsor_type_enum'), nullable=False)
    industry = Column(String(256), nullable=False)
    overall_budget = Column(Float, nullable=False,default=0.0)

    __mapper_args__ = {
        'polymorphic_identity': 'sponsor',
        'polymorphic_on': sponsor_type
    }

    def __init__(self, username, passhash, name=None, industry=None,overall_budget=0.0):
        super().__init__(username, passhash, name)
        self.user_type='sponsor'
        self.sponsor_type = 'sponsor'
        self.industry = industry
        self.overall_budget = overall_budget

    sponsor_campaigns = relationship('Campaign', backref='sponsor_relation', overlaps="sponsor_campaigns,sponsor_relation")

class NicheEnum(enum.Enum):
    COOKING = 'COOKING'
    TECHNOLOGY = 'TECHNOLOGY'
    EDUCATION = 'EDUCATION'
    FASHION = 'FASHION '
    GAMING = 'GAMING'
    VLOGGING = 'VLOGGING '
    TRAVEL='TRAVEL'
    FITNESS='FITNESS'
    HEALTH='HEALTH'
    BEAUTY='BEAUTY'


class Influencer(User):
    __tablename__ = 'influencer'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    influencer_type = Column(Enum('influencer', name='influencer_type_enum'), nullable=False)
    platform = Column(Enum('Youtube', 'Instagram', 'Facebook', 'Linkedin', name='platform_enum'), nullable=False)
    niche = Column(Enum(NicheEnum), nullable=False)
    reach = Column(Integer, nullable=True)
    followers = db.Column(db.Integer, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'influencer',
        'polymorphic_on': influencer_type
    }

    def __init__(self, username, passhash, name=None, platform=None, niche=None, reach=None):
        super().__init__(username, passhash, name)
        self.user_type='influencer'
        self.influencer_type = 'influencer'
        self.platform = platform
        self.niche = niche
        self.reach = reach
    @property
    def niche_display(self):
        return self.niche.value
    def is_authenticated(self):
        return True  

    def is_active(self):
        return True  

    def is_anonymous(self):
        return False  

    def get_id(self):
        return str(self.id)

    influencer_ad_requests = relationship('AdRequest', backref='influencer_relation', overlaps="influencer_ad_requests,influencer_relation")


class InfluencerDetails(db.Model):
    __tablename__ = 'influencer_details'
    id=Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey('influencer.id'), unique=True)
    profile_picture = Column(String(256), nullable=True)
    earnings = Column(Float, default=0.0)
    rating= Column(Float, default=0.0)

    influencer=relationship('Influencer',backref='details')



class Campaign(db.Model):
    __tablename__ = 'campaign'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False,default=date.today())
    end_date = Column(Date, nullable=False,default=lambda:date.today()+timedelta(days=30))
    budget = Column(Float, nullable=False,default=0.0)
    visibility = Column(Enum('public', 'private', name='visibility_enum'), nullable=False, default='public')
    sponsor_id = Column(Integer, ForeignKey('sponsor.id'), nullable=False)
    flagged = Column(Boolean, default=False)
    status = Column(String(20), nullable=False,default='In Progress')
    niche = db.Column(db.Enum(NicheEnum), nullable=True)
    completion_status = Column(Boolean, default=False)

    sponsor = relationship('Sponsor', backref='campaigns', overlaps="sponsor_campaigns,sponsor_relation")

class AdRequest(db.Model):
    __tablename__ = 'ad_request'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaign.id'), nullable=False)
    influencer_id = Column(Integer, ForeignKey('influencer.id',ondelete='CASCADE'), nullable=False)
    requirements = Column(Text, nullable=True)
    payment_amount = Column(Float, nullable=False)
    status = Column(Enum('Pending', 'Accepted', 'Rejected', name='status_enum'), nullable=False, default='Pending')

    campaign = relationship('Campaign', backref='ad_requests')
    influencer = relationship('Influencer',backref=backref('ad_requests', cascade='all, delete-orphan'), overlaps="influencer_ad_requests,influencer_relation")

def update_user_types():
    with app.app_context():
        users = User.query.all()
        for user in users:
            if user.user_type is None:
                if Admin.query.filter_by(id=user.id).first():
                    user.user_type = 'admin'
                elif Sponsor.query.filter_by(id=user.id).first():
                    user.user_type = 'sponsor'
                elif Influencer.query.filter_by(id=user.id).first():
                    user.user_type = 'influencer'
                else:
                    user.user_type = 'user'
                db.session.add(user)
        db.session.commit()




with app.app_context():
        db.create_all()
        update_user_types()
    