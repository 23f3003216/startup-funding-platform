from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
import config
from extensions import db

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)

from models import User  # import after db init

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

import routes  # import routes here

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # optional if using migrations
    app.run(debug=True)
