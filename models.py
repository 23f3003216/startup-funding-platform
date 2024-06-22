from app import app,db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Boolean, Enum, Integer, Column, ForeignKey, Text, Date, Float
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True)
    passhash = Column(String(256), nullable=False)
    name = Column(String(64), nullable=True)
    flagged = Column(Boolean, default=False)
    user_type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }
 
    def __init__(self, username, passhash, name=None):
        self.username = username
        self.passhash = passhash
        self.name = name

    def is_administrator(self):
        return False

class Admin(User):
    __tablename__ = 'admin'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

    def __init__(self, username, passhash, name=None):
        super().__init__(username, passhash, name)

    def is_administrator(self):
        return True

class Sponsor(User):
    __tablename__ = 'sponsor'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    sponsor_type = Column(Enum('sponsor', name='sponsor_type_enum'), nullable=False)
    industry = Column(String(256), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'sponsor',
        'polymorphic_on': sponsor_type
    }

    def __init__(self, username, passhash, name=None, industry=None):
        super().__init__(username, passhash, name)
        self.sponsor_type = 'sponsor'
        self.industry = industry

    sponsor_campaigns = relationship('Campaign', backref='sponsor_relation', overlaps="sponsor_campaigns,sponsor_relation")

class Influencer(User):
    __tablename__ = 'influencer'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    influencer_type = Column(Enum('influencer', name='influencer_type_enum'), nullable=False)
    platform = Column(Enum('Youtube', 'Instagram', 'Facebook', 'Linkedin', name='platform_enum'), nullable=False)
    category = Column(String(64), nullable=False)
    niche = Column(String(64), nullable=False)
    reach = Column(Integer, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'influencer',
        'polymorphic_on': influencer_type
    }

    def __init__(self, username, passhash, name=None, platform=None, category=None, niche=None, reach=None):
        super().__init__(username, passhash, name)
        self.influencer_type = 'influencer'
        self.platform = platform
        self.category = category
        self.niche = niche
        self.reach = reach

    influencer_ad_requests = relationship('AdRequest', backref='influencer_relation', overlaps="influencer_ad_requests,influencer_relation")

class Campaign(db.Model):
    __tablename__ = 'campaign'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Float, nullable=False)
    visibility = Column(Enum('public', 'private', name='visibility_enum'), nullable=False, default='public')
    sponsor_id = Column(Integer, ForeignKey('sponsor.id'), nullable=False)
    flagged = Column(Boolean, default=False)

    sponsor = relationship('Sponsor', backref='campaigns', overlaps="sponsor_campaigns,sponsor_relation")

class AdRequest(db.Model):
    __tablename__ = 'ad_request'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaign.id'), nullable=False)
    influencer_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    requirements = Column(Text, nullable=True)
    payment_amount = Column(Float, nullable=False)
    status = Column(Enum('Pending', 'Accepted', 'rejected', name='status_enum'), nullable=False, default='Pending')

    campaign = relationship('Campaign', backref='ad_requests')
    influencer = relationship('Influencer', backref='ad_requests', overlaps="influencer_ad_requests,influencer_relation")

with app.app_context():
        db.create_all()
    