from flask import render_template, redirect, url_for, request, flash
from app import app, db
from models import User, Admin, Investor, Startup, FundingCampaign, PitchRequest
from models import SectorEnum

from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date

# --- Authentication Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.passhash, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            # Redirect based on user type
            if user.user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.user_type == 'investor':
                return redirect(url_for('investor_dashboard'))
            elif user.user_type == 'startup':
                return redirect(url_for('startup_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

# --- Home Page ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Admin Dashboard ---
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_administrator():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    # Example: Show stats
    total_users = User.query.count()
    total_investors = Investor.query.count()
    total_startups = Startup.query.count()
    total_campaigns = FundingCampaign.query.count()
    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_investors=total_investors,
                           total_startups=total_startups,
                           total_campaigns=total_campaigns)
from flask import abort

def check_flagged_investor():
    if current_user.user_type == 'investor' and current_user.flagged:
        flash('You have been flagged by the admin and cannot access this section.', 'danger')
        return True
    return False
def check_flagged_startup():
    if current_user.user_type == 'startup' and current_user.flagged:
        flash('You have been flagged by the admin and cannot access this section.', 'danger')
        return True
    return False

# --- Investor Dashboard ---
@app.route('/investor/dashboard')
@login_required
def investor_dashboard():
    if current_user.user_type != 'investor':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    if check_flagged_investor():
        return render_template('investor_flagged.html')
    
    campaigns = FundingCampaign.query.filter_by(investor_id=current_user.id).all()

    # Get all pitches related to these campaigns
    campaign_ids = [c.id for c in campaigns]
    pitches = PitchRequest.query.filter(PitchRequest.campaign_id.in_(campaign_ids)).all()

    return render_template('investor_dashboard.html', campaigns=campaigns, pitches=pitches)


# Create new funding campaign
@app.route('/investor/campaign/new', methods=['GET', 'POST'])
@login_required
def new_funding_campaign():
    if current_user.user_type != 'investor':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    if check_flagged_investor():
        return render_template('investor_flagged.html')
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        sector = request.form['sector']
        budget = float(request.form['budget'])
        deadline = request.form['deadline']  # Expecting 'YYYY-MM-DD'

        # Budget check vs overall_budget
        if budget > current_user.overall_budget:
            flash('Campaign budget exceeds your overall budget.', 'danger')
            return redirect(url_for('new_funding_campaign'))

        campaign = FundingCampaign(
            title=title,
            description=description,
            sector=sector,
            budget=budget,
            deadline=date.fromisoformat(deadline),
            investor_id=current_user.id
        )
        db.session.add(campaign)
        db.session.commit()
        flash('Funding campaign created.', 'success')
        return redirect(url_for('investor_dashboard'))
    
    sectors = [e.value for e in SectorEnum]
    return render_template('new_funding_campaign.html', sectors=sectors)

from models import FundingCampaign  # make sure this import is present

@app.route('/startup/dashboard', methods=['GET'])
@login_required
def startup_dashboard():
    if current_user.user_type != 'startup':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    if check_flagged_startup():
        return render_template('startup_flagged.html')

    # 🔍 Get search parameters
    campaign_title = request.args.get('campaign_title')
    status = request.args.get('status')
    min_amount = request.args.get('min_amount')

    # 🔎 Base query: all pitches by this startup
    query = PitchRequest.query.filter_by(startup_id=current_user.id)

    # 🧠 Join with FundingCampaign for filtering by title
    if campaign_title:
        query = query.join(FundingCampaign).filter(FundingCampaign.title.ilike(f"%{campaign_title}%"))

    if status:
        query = query.filter(PitchRequest.status == status)

    if min_amount:
        try:
            query = query.filter(PitchRequest.proposed_amount >= float(min_amount))
        except ValueError:
            pass  # ignore invalid input

    pitch_requests = query.all()

    return render_template('startup_dashboard.html', pitch_requests=pitch_requests)



# View all funding campaigns to pitch on
@app.route('/startup/campaigns')
@login_required
def view_campaigns():
    if current_user.user_type != 'startup':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    if check_flagged_startup():
        return render_template('startup_flagged.html')

    campaigns = FundingCampaign.query.filter_by(is_completed=False).all()
    return render_template('campaigns_list.html', campaigns=campaigns)

# Submit pitch request
@app.route('/startup/pitch/new/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def submit_pitch(campaign_id):
    if current_user.user_type != 'startup':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    if check_flagged_startup():
        return render_template('startup_flagged.html')

    campaign = FundingCampaign.query.get_or_404(campaign_id)

    if request.method == 'POST':
        pitch_text = request.form['pitch_text']
        proposed_amount = float(request.form['proposed_amount'])

        # Check if proposed amount is reasonable (optional)
        if proposed_amount > campaign.budget:
            flash('Proposed amount exceeds campaign budget.', 'danger')
            return redirect(url_for('submit_pitch', campaign_id=campaign_id))

        pitch = PitchRequest(
            campaign_id=campaign.id,
            startup_id=current_user.id,
            pitch_text=pitch_text,
            proposed_amount=proposed_amount,
            status='pending'
        )
        db.session.add(pitch)
        db.session.commit()
        flash('Pitch submitted successfully.', 'success')
        return redirect(url_for('startup_dashboard'))

    return render_template('submit_pitch.html', campaign=campaign)

# --- Additional routes for pitch request status updates by investors ---
@app.route('/investor/pitch/<int:pitch_id>/update', methods=['POST'])
@login_required
def update_pitch_status(pitch_id):
    if current_user.user_type != 'investor':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    if check_flagged_investor():
        return render_template('investor_flagged.html')

    pitch = PitchRequest.query.get_or_404(pitch_id)

    # Confirm that pitch belongs to one of this investor's campaigns
    if pitch.campaign_relation.investor_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('investor_dashboard'))

    new_status = request.form['status']
    if new_status not in ['pending', 'accepted', 'rejected', 'completed']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('investor_dashboard'))

    pitch.status = new_status
    db.session.commit()
    flash(f'Pitch status updated to {new_status}.', 'success')
    return redirect(url_for('investor_dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already taken by another user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username already taken.', 'danger')
            return redirect(url_for('profile'))

        current_user.username = username
        if password:
            current_user.passhash = generate_password_hash(password)

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        if user_type == 'investor':
            industry = request.form.get('industry')
            overall_budget = float(request.form.get('overall_budget', 0))
            # create investor user
            investor = Investor(
                username=username,
                passhash=generate_password_hash(password),
                name=username,
                industry=industry,
                overall_budget=overall_budget
            )
            db.session.add(investor)
            db.session.commit()

        elif user_type == 'startup':
            platform = request.form.get('platform')
            sector = request.form.get('sector')
            traction = request.form.get('traction')
            revenue = request.form.get('revenue')

            startup = Startup(
                username=username,
                passhash=generate_password_hash(password),
                name=username,
                platform=platform,
                sector=sector,
                traction=int(traction) if traction else None,
                revenue=float(revenue) if revenue else None
            )
            db.session.add(startup)
            db.session.commit()

        else:
            # Handle invalid user_type or other user types if any
            pass

        flash("Registration successful!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


from models import Admin  # not User
from werkzeug.security import generate_password_hash

@app.route('/create_admin')
def create_admin():
    from models import db

    if Admin.query.filter_by(username='admin').first():
        return "Admin already exists."

    admin_user = Admin(
        username='admin',
        passhash=generate_password_hash('admin123')
    )
    db.session.add(admin_user)
    db.session.commit()
    return "Admin user created successfully."


# Route to manage startups (Admin only)
@app.route('/admin/manage_startups')
@login_required
def manage_startups():
    if not current_user.is_administrator():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    startups = Startup.query.all()
    return render_template('manage_startups.html', startups=startups)

# Route to manage campaigns (Admin only)
@app.route('/admin/manage_campaigns')
@login_required
def manage_campaigns():
    if not current_user.is_administrator():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    campaigns = FundingCampaign.query.all()
    return render_template('manage_campaigns.html', campaigns=campaigns)

# Route to view reports (Admin only)
@app.route('/admin/reports')
@login_required
def admin_reports():
    if not current_user.is_administrator():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    # You can compute whatever statistics you want here
    total_users = User.query.count()
    total_campaigns = FundingCampaign.query.count()
    total_pitches = PitchRequest.query.count()
    return render_template('admin_reports.html', total_users=total_users,
                           total_campaigns=total_campaigns,
                           total_pitches=total_pitches)

@app.route('/admin/manage_investors')
@login_required
def manage_investors():
    if not current_user.is_administrator():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    investors = User.query.filter_by(user_type='investor').all()
    return render_template('manage_investors.html', investors=investors)



@app.route('/campaign/<int:campaign_id>')
@login_required
def view_campaign(campaign_id):
    campaign = FundingCampaign.query.get_or_404(campaign_id)

    amount_raised = db.session.query(db.func.coalesce(db.func.sum(PitchRequest.proposed_amount), 0)) \
        .filter(PitchRequest.campaign_id == campaign_id, PitchRequest.status == 'accepted').scalar()

    return render_template('view_campaign.html', campaign=campaign, amount_raised=amount_raised)

@app.route('/investor/campaign/edit/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def edit_funding_campaign(campaign_id):
    if current_user.user_type != 'investor':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    if check_flagged_investor():
        return render_template('investor_flagged.html')
    
    campaign = FundingCampaign.query.get_or_404(campaign_id)

    if campaign.investor_id != current_user.id:
        flash('You cannot edit this campaign.', 'danger')
        return redirect(url_for('investor_dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        sector = request.form['sector']
        budget = float(request.form['budget'])
        deadline = request.form['deadline']

        # Check budget vs overall_budget (allow update if within budget)
        if budget > current_user.overall_budget:
            flash('Budget exceeds your overall budget.', 'danger')
            return redirect(url_for('edit_funding_campaign', campaign_id=campaign_id))

        campaign.title = title
        campaign.description = description
        campaign.sector = sector
        campaign.budget = budget
        campaign.deadline = date.fromisoformat(deadline)

        db.session.commit()
        flash('Campaign updated successfully.', 'success')
        return redirect(url_for('investor_dashboard'))

    sectors = [e.value for e in SectorEnum]
    return render_template('edit_funding_campaign.html', campaign=campaign, sectors=sectors)

@app.route('/investor/campaign/delete/<int:campaign_id>', methods=['POST'])
@login_required
def delete_funding_campaign(campaign_id):
    if current_user.user_type != 'investor':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    if check_flagged_investor():
        return render_template('investor_flagged.html')

    campaign = FundingCampaign.query.get_or_404(campaign_id)

    if campaign.investor_id != current_user.id:
        flash('You cannot delete this campaign.', 'danger')
        return redirect(url_for('investor_dashboard'))

    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully.', 'success')
    return redirect(url_for('investor_dashboard'))

@app.route('/investor/pitch/<int:pitch_id>/pay', methods=['GET', 'POST'])
@login_required
def pay_pitch(pitch_id):
    if current_user.user_type != 'investor':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    if check_flagged_investor():
        return render_template('investor_flagged.html')

    pitch = PitchRequest.query.get_or_404(pitch_id)
    campaign = pitch.campaign_relation

    if campaign.investor_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('investor_dashboard'))

    if request.method == 'POST':
        amount = float(request.form['amount'])
        # For dummy payment just accept amount and show success message
        if amount <= 0:
            flash('Amount must be positive.', 'danger')
            return redirect(url_for('pay_pitch', pitch_id=pitch_id))
        if amount > pitch.proposed_amount:
            flash('Payment amount exceeds proposed amount.', 'danger')
            return redirect(url_for('pay_pitch', pitch_id=pitch_id))

        # Here you can record payment in DB if you have payment model
        flash(f'Dummy payment of ₹{amount} to startup {pitch.startup_relation.username} successful!', 'success')
        return redirect(url_for('investor_dashboard'))

    return render_template('pay_pitch.html', pitch=pitch)

@app.route('/investor/pitch/<int:pitch_id>/mark_paid', methods=['POST'])
@login_required
def mark_pitch_paid(pitch_id):
    pitch = PitchRequest.query.get_or_404(pitch_id)
    
    # Only the investor who owns the campaign can mark it as paid
    if pitch.campaign_relation.investor_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('investor_dashboard'))
    if check_flagged_investor():
        return render_template('investor_flagged.html')
    
    pitch.is_paid = True
    db.session.commit()
    flash("Payment marked as done.", "success")
    return redirect(url_for('investor_dashboard'))

@app.route('/investor/pitch/<int:pitch_id>/make_payment', methods=['POST'])
@login_required
def make_payment(pitch_id):
    if current_user.user_type != 'investor':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    if check_flagged_investor():
        return render_template('investor_flagged.html')

    pitch = PitchRequest.query.get_or_404(pitch_id)

    # Confirm the campaign belongs to the current investor
    if pitch.campaign_relation.investor_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('investor_dashboard'))

    pitch.is_paid = True
    db.session.commit()
    flash('Payment marked as completed.', 'success')
    return redirect(url_for('investor_dashboard'))

from flask import jsonify

# Utility decorator for admin check
def admin_required(f):
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_administrator():
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Flag/Unflag Investor
@app.route('/admin/investor/<int:investor_id>/flag', methods=['POST'])
@admin_required
def flag_investor(investor_id):
    investor = Investor.query.get_or_404(investor_id)
    investor.flagged = not investor.flagged  # toggle flag
    db.session.commit()
    status = 'flagged' if investor.flagged else 'unflagged'
    flash(f'Investor {investor.name} has been {status}.', 'success')
    return redirect(url_for('manage_investors'))

# Delete Investor
@app.route('/admin/investor/<int:investor_id>/delete', methods=['POST'])
@admin_required
def delete_investor(investor_id):
    investor = Investor.query.get_or_404(investor_id)
    db.session.delete(investor)
    db.session.commit()
    flash(f'Investor {investor.name} has been deleted.', 'success')
    return redirect(url_for('manage_investors'))

# Flag/Unflag Startup
@app.route('/admin/startup/<int:startup_id>/flag', methods=['POST'])
@admin_required
def flag_startup(startup_id):
    startup = Startup.query.get_or_404(startup_id)
    startup.flagged = not startup.flagged
    db.session.commit()
    status = 'flagged' if startup.flagged else 'unflagged'
    flash(f'Startup {startup.name} has been {status}.', 'success')
    return redirect(url_for('manage_startups'))

# Delete Startup
@app.route('/admin/startup/<int:startup_id>/delete', methods=['POST'])
@admin_required
def delete_startup(startup_id):
    startup = Startup.query.get_or_404(startup_id)
    db.session.delete(startup)
    db.session.commit()
    flash(f'Startup {startup.name} has been deleted.', 'success')
    return redirect(url_for('manage_startups'))

@app.route('/find_startups', methods=['GET'])
def find_startups():
    sector = request.args.get('sector')
    revenue = request.args.get('revenue')
    traction = request.args.get('traction')
    platform = request.args.get('platform')

    # Build base query
    query = Startup.query

    if sector:
        query = query.filter(Startup.sector.ilike(f"%{sector}%"))
    if revenue:
        query = query.filter(Startup.revenue >= float(revenue))
    if traction:
        query = query.filter(Startup.traction.ilike(f"%{traction}%"))
    if platform:
        query = query.filter(Startup.platform.ilike(f"%{platform}%"))

    startups = query.all()

    return render_template('find_startups.html', startups=startups)
