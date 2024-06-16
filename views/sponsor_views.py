from app import app
from flask import Flask,render_template,abort,session
from models import is_sponsor
app=Flask(__name__)
@app.route('/sponsor-dashboard')
def sponsor_dashboard():
    if 'sponsor_username' not in session or not is_sponsor(session['sponsor_username']):
        return abort(403)
    return render_template('sponsor_dashboard.html')
