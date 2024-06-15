from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

import config
db = SQLAlchemy(app)

import routes

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
