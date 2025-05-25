from datetime import date, timedelta
import enum
from sqlalchemy import String, Boolean, Enum, Integer, Column, ForeignKey, Text, Date, Float
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from extensions import db

# 🧠 Base User Class
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True)
    passhash = Column(String(256), nullable=False)
    name = Column(String(64), nullable=True)
    flagged = Column(Boolean, default=False)
    user_type = Column(String(50), nullable=False, default='user')
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def __init__(self, username, passhash, name=None):
        self.username = username
        self.passhash = passhash
        self.name = name
        self.user_type = 'user'

    def is_administrator(self):
        return False

# 👑 Admin
class Admin(User):
    __tablename__ = 'admin'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    def __init__(self, username, passhash, name=None):
        super().__init__(username, passhash, name)
        self.user_type = 'admin'

    def is_administrator(self):
        return True

# 💰 Investor
class Investor(User):
    __tablename__ = 'investor'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    investor_type = Column(Enum('investor', name='investor_type_enum'), nullable=False)
    industry = Column(String(256), nullable=False)
    overall_budget = Column(Float, nullable=False, default=0.0)
    email = Column(String(120), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    flagged = db.Column(db.Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'investor',
        'polymorphic_on': investor_type
    }

    def __init__(self, username, passhash, name=None, industry=None, overall_budget=0.0, email=None, phone=None):
        super().__init__(username, passhash, name)
        self.user_type = 'investor'
        self.investor_type = 'investor'
        self.industry = industry
        self.overall_budget = overall_budget
        self.email = email
        self.phone = phone


    investor_campaigns = relationship('FundingCampaign', backref='investor_relation', overlaps="investor_campaigns,investor_relation")

# 📊 Sector Enum
class SectorEnum(enum.Enum):
    AI = 'AI'
    FINTECH = 'FINTECH'
    EDTECH = 'EDTECH'
    HEALTHCARE = 'HEALTHCARE'
    AGRITECH = 'AGRITECH'
    SUSTAINABILITY = 'SUSTAINABILITY'
    LOGISTICS = 'LOGISTICS'
    ECOMMERCE = 'ECOMMERCE'

# 🚀 Startup
class Startup(User):
    __tablename__ = 'startup'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    startup_type = Column(Enum('startup', name='startup_type_enum'), nullable=False)
    platform = Column(Enum('Website', 'App', 'Both', name='startup_platform_enum'), nullable=False)
    sector = Column(Enum(SectorEnum), nullable=False)
    traction = Column(Integer, nullable=True)
    revenue = Column(Float, nullable=True)
    email = Column(String(120), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    flagged = db.Column(db.Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'startup',
        'polymorphic_on': startup_type
    }

    def __init__(self, username, passhash, name=None, platform=None, sector=None, traction=None, revenue=None, email=None, phone=None):
        super().__init__(username, passhash, name)
        self.user_type = 'startup'
        self.startup_type = 'startup'
        self.platform = platform
        self.sector = sector
        self.traction = traction
        self.revenue = revenue
        self.email = email
        self.phone = phone


    @property
    def sector_display(self):
        return self.sector.value

    def get_id(self):
        return str(self.id)

    startup_pitch_requests = relationship('PitchRequest', backref='startup_relation', overlaps="startup_pitch_requests,startup_relation")

# 📁 Startup Details
class StartupDetails(db.Model):
    __tablename__ = 'startup_details'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('startup.id'), unique=True)
    profile_picture = Column(String(256), nullable=True)
    earnings = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    valuation = Column(Float, nullable=True)

    startup = relationship('Startup', backref=backref('details', cascade='all,delete-orphan'))

# 💼 Funding Campaign (created by Investor)
class FundingCampaign(db.Model):
    __tablename__ = 'funding_campaign'
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    sector = Column(Enum(SectorEnum), nullable=False)
    budget = Column(Float, nullable=False)
    deadline = Column(Date, nullable=False)
    investor_id = Column(Integer, ForeignKey('investor.id'), nullable=False)
    is_completed = Column(Boolean, default=False)
    created_on = Column(Date, default=date.today)
    flagged = db.Column(db.Boolean, default=False)

    # Relationship: all pitch requests submitted for this campaign
    pitch_requests = relationship('PitchRequest', backref='campaign_relation', cascade='all, delete-orphan')

# 📤 Pitch Request (by Startups)
class PitchRequest(db.Model):
    __tablename__ = 'pitch_request'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('funding_campaign.id'), nullable=False)
    startup_id = Column(Integer, ForeignKey('startup.id'), nullable=False)
    pitch_text = Column(Text, nullable=True)
    proposed_amount = Column(Float, nullable=False)
    status = Column(Enum('pending', 'accepted', 'rejected', 'completed', name='pitch_status_enum'), default='pending')
    created_on = Column(Date, default=date.today)
    is_paid = db.Column(db.Boolean, default=False)

def update_user_types():
    for user in User.query.all():
        if isinstance(user, Admin):
            user.user_type = 'admin'
        elif isinstance(user, Investor):
            user.user_type = 'investor'
        elif isinstance(user, Startup):
            user.user_type = 'startup'
        else:
            user.user_type = 'user'
    db.session.commit()
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database tables created.")
        update_user_types()  
