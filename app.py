from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app = Flask(__name__)

import config
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import User,Campaign,AdRequest,Influencer,Sponsor,Admin
with app.app_context():
        db.create_all()

import routes

if __name__ == '__main__':
    app.run(debug=True)
