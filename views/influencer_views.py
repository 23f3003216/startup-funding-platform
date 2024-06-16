from app import app
from flask import Flask,render_template,abort,session
from models import is_influencer
app=Flask(__name__)
@app.route('/influencer-dashboard')
def influencer_dashboard():
    if 'influencer_username' not in session or not is_influencer(session['influencer_username']):
        return abort(403)
    return render_template('influencer_dashboard.html')
