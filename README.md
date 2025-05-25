# Startup Funding Platform

## Project Statement

Startup Funding Platform is a web application designed to connect Investors and Startups, enabling investors to discover promising startups to fund, and startups to showcase their business and funding needs.


## Approach

- Created separate registration forms for investors and startups.
- Implemented a common login system for all user roles.
- Designed models with proper relationships such as investors, startups, funding campaigns, and pitch requests.
- Investors can search for startups based on sector, revenue, traction, and platform.
- Startups can create and manage funding campaigns, submit pitch requests, and track their status.
- Investors can view startups’ details and pitch requests, accept or reject funding proposals.
- Added dashboard views for both investors and startups to monitor their activities.
- Implemented role-based access control and authentication using Flask-Login.
- Public and private campaigns are handled, enabling startups to control visibility of their funding needs.
- Provided budgeting features for campaigns and tracked funding progress.
- Designed and implemented a clean, responsive frontend using Bootstrap and Jinja2 templates.
- Implemented basic placeholder payment functionality for funding transactions.
- Ensured database updates reflect all key actions and status changes throughout the platform.



## Frameworks and Libraries Used

- Flask  
- SQLAlchemy  
- Jinja2  
- WTForms  
- Flask-Bootstrap  
- Flask-WTF  
- Flask-Login  
- werkzeug.security (for password hashing)  
- Flask-Migrate  



## ER Diagram Summary

- **User**  
  - PK: id  
  - Attributes: username, password_hash, name, user_type  

- **Investor (inherits User)**  
  - PK: id (FK to User.id)  
  - Attributes: investor_type, industry  

- **Startup (inherits User)**  
  - PK: id (FK to User.id)  
  - Attributes: sector, revenue, traction, platform  

- **FundingCampaign**  
  - PK: id  
  - Attributes: title, description, start_date, end_date, budget, visibility, startup_id, status, niche  

- **PitchRequest**  
  - PK: id  
  - Attributes: campaign_id, investor_id, proposed_amount, status, pitch_text  


