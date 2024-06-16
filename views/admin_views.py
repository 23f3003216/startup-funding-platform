from app import app
from flask import Flask,render_template,abort,request,make_response
from models import is_admin
app=Flask(__name__)
ADMIN_USERNAME='admin'
ADMIN_PASSWORD='secret_password'
@app.route('/admin-dashboard')
def admin_dashboard():
    authorising=request.authorisation
    if not authorising or authorising.username != ADMIN_USERNAME or authorising.password != ADMIN_PASSWORD:
      response = make_response('Unauthorized access.', 401)
      response.headers['WWW-Authenticate'] = 'Basic realm="Admin Login"'
      return response
    return render_template('admin_dashboard.html')