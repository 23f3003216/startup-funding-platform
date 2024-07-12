from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, current_user, login_required,UserMixin

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


import config
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import User,Campaign,AdRequest,Influencer,Sponsor,Admin,InfluencerDetails
from routes import setup
with app.app_context():
        db.create_all()


import routes
from routes import stats_bp
app.register_blueprint(stats_bp)

if __name__ == '__main__':
    setup()
    login_manager.init_app(app) 
    app.run(debug=True)
