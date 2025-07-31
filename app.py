from flask import Flask, render_template, request, redirect, session, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from functools import wraps
from sqlalchemy.orm import joinedload
from flask import abort
from flask import flash

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'  # Secret key for sessions and security
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobportal.db'  # Database configuration (SQLite)
db = SQLAlchemy(app)


# ===================
# Database Models
# ===================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # Unique username
    email = db.Column(db.String(120), unique=True, nullable=False)    # Unique email
    password = db.Column(db.String(200), nullable=False)  # Hashed password
    role = db.Column(db.String(20), nullable=False)  # Role of user: jobseeker, employer, or admin


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    salary = db.Column(db.String(20))
    location = db.Column(db.String(50))
    company = db.Column(db.String(50))
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Relation to employer (User)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job = db.relationship('Job', backref='applications')  # Relationship to job


# ===================
# Hot Jobs Data (Backend copy for lookup)
# ===================
# Static list of demo "hot jobs" for display and applications simulation
hot_jobs = [
    {"id": 1, "title": "Frontend Developer", "description": "Work with React.js and build responsive UIs.", "type": "Full Time", "category": "Development", "location": "Bangalore", "salary": "₹8-10 LPA", "company": "TechNova", "experience": "2-4 years"},
    {"id": 2, "title": "Backend Developer", "description": "Develop APIs using Node.js and Express.", "type": "Full Time", "category": "Development", "location": "Hyderabad", "salary": "₹10-12 LPA", "company": "CodeBase", "experience": "2-4 years"},
    {"id": 3, "title": "UI/UX Designer", "description": "Design modern and intuitive user interfaces.", "type": "Full Time", "category": "Design", "location": "Mumbai", "salary": "₹6-8 LPA", "company": "DesignHub", "experience": "3-5 years"},
    {"id": 4, "title": "DevOps Engineer", "description": "Manage CI/CD pipelines and cloud infra.", "type": "Full Time", "category": "DevOps", "location": "Remote", "salary": "₹9-12 LPA", "company": "CloudOps", "experience": "3-6 years"},
    {"id": 5, "title": "Data Analyst", "description": "Analyze data and provide business insights.", "type": "Full Time", "category": "Data", "location": "Pune", "salary": "₹7-9 LPA", "company": "DataWorks", "experience": "1-3 years"},
    {"id": 6, "title": "Machine Learning Engineer", "description": "Build ML models and deploy in production.", "type": "Full Time", "category": "AI/ML", "location": "Bangalore", "salary": "₹12-15 LPA", "company": "AI Labs", "experience": "5+ years"},
    {"id": 7, "title": "Product Manager", "description": "Lead cross-functional teams to build products.", "type": "Full Time", "category": "Product", "location": "Gurgaon", "salary": "₹15-18 LPA", "company": "Prodify", "experience": "6+ years"},
    {"id": 8, "title": "QA Tester", "description": "Perform manual and automation testing.", "type": "Full Time", "category": "Testing", "location": "Chennai", "salary": "₹5-7 LPA", "company": "BugSquashers", "experience": "0-2 years"},
    {"id": 9, "title": "Content Writer", "description": "Write blogs, website content, and case studies.", "type": "Full Time", "category": "Content", "location": "Remote", "salary": "₹4-5 LPA", "company": "WriteWave", "experience": "1-3 years"},
    {"id": 10, "title": "HR Executive", "description": "Handle recruitment and employee engagement.", "type": "Full Time", "category": "HR", "location": "Noida", "salary": "₹4-6 LPA", "company": "PeopleFirst", "experience": "1-3 years"},
    {"id": 11, "title": "Digital Marketing Executive", "description": "Run paid campaigns and manage SEO.", "type": "Full Time", "category": "Marketing", "location": "Delhi", "salary": "₹5-7 LPA", "company": "GrowthHacks", "experience": "1-3 years"},
    {"id": 12, "title": "Cloud Architect", "description": "Design and implement cloud solutions.", "type": "Full Time", "category": "Cloud", "location": "Bangalore", "salary": "₹18-22 LPA", "company": "SkyNet", "experience": "6+ years"},
    {"id": 13, "title": "Sales Manager", "description": "Drive sales strategies and lead teams.", "type": "Full Time", "category": "Sales", "location": "Mumbai", "salary": "₹10-14 LPA", "company": "SellWell", "experience": "4-7 years"},
    {"id": 14, "title": "Business Analyst", "description": "Analyze business processes and suggest solutions.", "type": "Full Time", "category": "Business", "location": "Chandigarh", "salary": "₹8-10 LPA", "company": "BizConsult", "experience": "3-5 years"},
    {"id": 15, "title": "Customer Support Executive", "description": "Support customers via chat, mail, and calls.", "type": "Full Time", "category": "Support", "location": "Pune", "salary": "₹3.5-5 LPA", "company": "HelpDeskPro", "experience": "0-1 years"},
    {"id": 16, "title": "IT Support Engineer", "description": "Provide hardware and software support.", "type": "Full Time", "category": "IT", "location": "Ahmedabad", "salary": "₹4-6 LPA", "company": "SysCare", "experience": "1-3 years"},
    {"id": 17, "title": "Graphic Designer", "description": "Create visuals for digital platforms.", "type": "Full Time", "category": "Design", "location": "Kolkata", "salary": "₹4-6 LPA", "company": "CreativeCore", "experience": "1-3 years"},
    {"id": 18, "title": "Android Developer", "description": "Build apps with Kotlin and Java.", "type": "Full Time", "category": "Mobile", "location": "Hyderabad", "salary": "₹6-8 LPA", "company": "AppStorm", "experience": "2-4 years"},
    {"id": 19, "title": "iOS Developer", "description": "Develop iOS apps with Swift.", "type": "Full Time", "category": "Mobile", "location": "Chennai", "salary": "₹7-9 LPA", "company": "SwiftTech", "experience": "2-4 years"},
    {"id": 20, "title": "Video Editor", "description": "Edit and produce marketing videos.", "type": "Full Time", "category": "Media", "location": "Mumbai", "salary": "₹3.5-5 LPA", "company": "VidEditz", "experience": "1-3 years"},
    {"id": 21, "title": "SEO Specialist", "description": "Optimize site rankings and content.", "type": "Full Time", "category": "Marketing", "location": "Delhi", "salary": "₹4-6 LPA", "company": "RankHigh", "experience": "2-4 years"},
    {"id": 22, "title": "Social Media Manager", "description": "Manage content and grow online presence.", "type": "Full Time", "category": "Marketing", "location": "Remote", "salary": "₹5-7 LPA", "company": "Socioly", "experience": "2-5 years"},
    {"id": 23, "title": "Technical Writer", "description": "Write product guides and documentation.", "type": "Full Time", "category": "Content", "location": "Bangalore", "salary": "₹6-8 LPA", "company": "DocuTech", "experience": "3-5 years"},
    {"id": 24, "title": "Cybersecurity Analyst", "description": "Protect systems from cyber threats.", "type": "Full Time", "category": "Security", "location": "Gurgaon", "salary": "₹10-13 LPA", "company": "SecureNet", "experience": "4-7 years"},
    {"id": 25, "title": "AI Researcher", "description": "Work on NLP and computer vision models.", "type": "Full Time", "category": "AI/ML", "location": "Pune", "salary": "₹15-20 LPA", "company": "AIThinkTank", "experience": "6+ years"},
    {"id": 26, "title": "Project Coordinator", "description": "Coordinate tasks and maintain timelines.", "type": "Full Time", "category": "Management", "location": "Chennai", "salary": "₹5-7 LPA", "company": "PlanIt", "experience": "2-4 years"},
    {"id": 27, "title": "Technical Support Engineer", "description": "Resolve client issues and provide tech support.", "type": "Full Time", "category": "Support", "location": "Bangalore", "salary": "₹4-6 LPA", "company": "TechHelp", "experience": "1-3 years"},
    {"id": 28, "title": "Recruiter", "description": "Source and screen potential candidates.", "type": "Full Time", "category": "HR", "location": "Jaipur", "salary": "₹4.5-6 LPA", "company": "HireRight", "experience": "2-4 years"},
    {"id": 29, "title": "Legal Associate", "description": "Draft contracts and handle legal work.", "type": "Full Time", "category": "Legal", "location": "Delhi", "salary": "₹6-8 LPA", "company": "LawVerse", "experience": "3-5 years"},
    {"id": 30, "title": "Operations Manager", "description": "Handle daily ops and process improvement.", "type": "Full Time", "category": "Operations", "location": "Kolkata", "salary": "₹9-11 LPA", "company": "Opsify", "experience": "5+ years"},
    {"id": 31, "title": "Game Developer", "description": "Develop engaging 2D/3D games.", "type": "Full Time", "category": "Gaming", "location": "Pune", "salary": "₹10-14 LPA", "company": "PlayZone", "experience": "3-5 years"},
    {"id": 32, "title": "Graphic Designer", "description": "Create marketing visuals and assets.", "type": "Part Time", "category": "Design", "location": "Delhi", "salary": "₹4-6 LPA", "company": "DesignMinds", "experience": "0-1 years"},
    {"id": 33, "title": "Security Analyst", "description": "Monitor and prevent cyber threats.", "type": "Full Time", "category": "Security", "location": "Mumbai", "salary": "₹9-11 LPA", "company": "CyberSafe", "experience": "4-7 years"},
    {"id": 34, "title": "Product Manager", "description": "Lead product development lifecycle.", "type": "Full Time", "category": "Management", "location": "Remote", "salary": "₹20-25 LPA", "company": "InnovateX", "experience": "6+ years"},
    {"id": 35, "title": "iOS Developer", "description": "Develop native iOS apps.", "type": "Full Time", "category": "Mobile", "location": "Chennai", "salary": "₹10-13 LPA", "company": "SwiftMob", "experience": "2-5 years"},
    {"id": 36, "title": "Android Developer", "description": "Create Android mobile applications.", "type": "Full Time", "category": "Mobile", "location": "Noida", "salary": "₹9-12 LPA", "company": "DroidBuild", "experience": "2-5 years"},
    {"id": 37, "title": "Digital Marketing Intern", "description": "Support online campaigns and content creation.", "type": "Internship", "category": "Marketing", "location": "Gurgaon", "salary": "₹10k/month", "company": "ClickBuzz", "experience": "Fresher"},
    {"id": 38, "title": "SEO Specialist", "description": "Improve website rankings and traffic.", "type": "Full Time", "category": "Marketing", "location": "Jaipur", "salary": "₹5-7 LPA", "company": "RankFirst", "experience": "2-4 years"},
    {"id": 39, "title": "Video Editor", "description": "Edit and produce video content.", "type": "Contract", "category": "Media", "location": "Mumbai", "salary": "₹6-8 LPA", "company": "FrameCut", "experience": "1-3 years"},
    {"id": 40, "title": "UI Designer", "description": "Design user interfaces for web and mobile.", "type": "Full Time", "category": "Design", "location": "Bangalore", "salary": "₹10-12 LPA", "company": "PixelEdge", "experience": "3-5 years"},
    {"id": 41, "title": "Customer Support Executive", "description": "Handle customer inquiries and support.", "type": "Full Time", "category": "Support", "location": "Ahmedabad", "salary": "₹3.5-5 LPA", "company": "HelpDeskPro", "experience": "0-2 years"},
    {"id": 42, "title": "Finance Analyst", "description": "Analyze financial performance and reports.", "type": "Full Time", "category": "Finance", "location": "Kolkata", "salary": "₹8-10 LPA", "company": "FinSharp", "experience": "2-4 years"},
    {"id": 43, "title": "Legal Associate", "description": "Assist in drafting and reviewing legal documents.", "type": "Full Time", "category": "Legal", "location": "Delhi", "salary": "₹7-9 LPA", "company": "LawBridge", "experience": "2-4 years"},
    {"id": 44, "title": "Business Analyst", "description": "Bridge business needs and tech solutions.", "type": "Full Time", "category": "Analysis", "location": "Hyderabad", "salary": "₹9-11 LPA", "company": "BizIntel", "experience": "3-5 years"},
    {"id": 45, "title": "Systems Engineer", "description": "Maintain and improve IT infrastructure.", "type": "Full Time", "category": "Infrastructure", "location": "Chandigarh", "salary": "₹6-8 LPA", "company": "InfraTech", "experience": "3-6 years"},
    {"id": 46, "title": "Robotics Engineer", "description": "Develop robotic automation systems.", "type": "Full Time", "category": "Engineering", "location": "Pune", "salary": "₹14-18 LPA", "company": "RoboCore", "experience": "5+ years"},
    {"id": 47, "title": "IT Support Specialist", "description": "Troubleshoot and resolve IT issues.", "type": "Full Time", "category": "Support", "location": "Nagpur", "salary": "₹4.5-6 LPA", "company": "FixTech", "experience": "1-3 years"},
    {"id": 48, "title": "Intern - HR & Admin", "description": "Support HR ops and documentation.", "type": "Internship", "category": "HR", "location": "Jaipur", "salary": "₹1.8-2.2 LPA", "company": "TeamCore", "experience": "Fresher"},
    {"id": 49, "title": "UX Researcher", "description": "Conduct user studies and usability tests.", "type": "Full Time", "category": "Design", "location": "Remote", "salary": "₹9-12 LPA", "company": "UserLab", "experience": "2-4 years"},
    {"id": 50, "title": "Salesforce Developer", "description": "Develop custom Salesforce solutions.", "type": "Full Time", "category": "CRM", "location": "Mumbai", "salary": "₹13-16 LPA", "company": "CRMWorld", "experience": "5+ years"}
]



def get_hot_job_by_id(hot_id):
    """Helper to find hot job by ID from hot_jobs list."""
    for job in hot_jobs:
        if job["id"] == hot_id:
            return job
    return None


# ===================
# Helpers
# ===================

def login_required(f):
    """Decorator to protect routes for logged-in users only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Redirect unauthorized users to login
        return f(*args, **kwargs)
    return decorated


# ===================
# Routes
# ===================

@app.route('/')
def home():
    """Home page showing job listings, supports search query filtering."""
    search_query = request.args.get('q', '').strip().lower()
    if search_query:
        # Filter jobs by title, company, or location matching search query (case-insensitive)
        jobs = Job.query.filter(
            Job.title.ilike(f'%{search_query}%') |
            Job.company.ilike(f'%{search_query}%') |
            Job.location.ilike(f'%{search_query}%')
        ).order_by(Job.id.desc()).all()
    else:
        # Show all jobs sorted by newest first
        jobs = Job.query.order_by(Job.id.desc()).all()
    return render_template('home.html', jobs=jobs, search_query=search_query)


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page. Handles form submission."""
    if request.method == 'POST':
        # Check if email already exists
        existing_user = User.query.filter_by(email=request.form['email']).first()
        if existing_user:
            return '⚠️ Email already registered.'
        # Hash password and create new user with form data
        hashed_pw = generate_password_hash(request.form['password'])
        new_user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=hashed_pw,
            role=request.form['role']
        )
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            # Handle race conditions for unique constraints
            db.session.rollback()
            return '⚠️ Username or email already exists.'
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page. Authenticates and creates session."""
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            # Successful login, save user info in session
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        return '❌ Invalid username or password.'
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page. Shows data based on user role."""
    role = session.get('role', None)
    user_id = session.get('user_id', None)

    if not role or not user_id:
        return redirect(url_for('login'))

    if role == 'employer':
        # For employer show jobs they posted
        jobs = Job.query.filter_by(employer_id=user_id).all()
        return render_template('dashboard.html', jobs=jobs)
    
    elif role == 'jobseeker':
        # For jobseeker show applications with eager loading jobs to avoid extra queries
        applications = Application.query.options(joinedload(Application.job)).filter_by(user_id=user_id).all()
        return render_template('dashboard.html', applications=applications)
    
    elif role == 'admin':
        # For admin show all users and all jobs
        users = User.query.all()
        jobs = Job.query.all()
        return render_template('dashboard.html', users=users, jobs=jobs)
    
    else:
        # Unknown roles are forbidden
        abort(403)


@app.route('/delete-job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    """Allows employers to delete their jobs."""
    if session.get('role') != 'employer':
        abort(403)  # Forbidden if not employer
    job = Job.query.get_or_404(job_id)
    if job.employer_id != session['user_id']:
        abort(403)  # Forbidden if not job owner
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    """Allows employers to post new jobs."""
    if session['role'] != 'employer':
        return '❌ Only employers can post jobs.'
    if request.method == 'POST':
        job = Job(
            title=request.form['title'],
            company=request.form['company'],
            location=request.form['location'],
            salary=request.form['salary'],
            description=request.form['description'],
            employer_id=session['user_id']
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('post_job.html')


@app.route('/apply/<job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    """
    Job application route supports two cases:
    - Hot jobs (demo jobs from in-memory list)
    - Database stored jobs
    """
    # Handle hot job application (id prefixed with 'hot-')
    if job_id.startswith("hot-"):
        try:
            hot_id = int(job_id.replace("hot-", ""))
        except:
            flash("Invalid hot job selected.", "warning")
            return redirect(url_for('home'))
        job = get_hot_job_by_id(hot_id)
        if not job:
            flash("Hot job not found.", "warning")
            return redirect(url_for('home'))
        if request.method == 'POST':
            if 'user_id' not in session or session['role'] != 'jobseeker':
                return redirect(url_for('login'))
            flash('Application submitted for hot job! (Note: hot jobs are demo only)', 'success')
            return redirect(url_for('dashboard'))
        return render_template('apply.html', job=job, is_hot=True)

    # Database job application case
    job = Job.query.get(int(job_id))
    if not job:
        flash("Job not found.", "warning")
        return redirect(url_for('home'))
    if request.method == 'POST':
        if 'user_id' not in session or session['role'] != 'jobseeker':
            return redirect(url_for('login'))
        # Prevent duplicate applications
        existing_application = Application.query.filter_by(job_id=job.id, user_id=session['user_id']).first()
        if existing_application:
            flash('You have already applied to this job.', 'warning')
            return redirect(url_for('dashboard'))
        application = Application(job_id=job.id, user_id=session['user_id'])
        db.session.add(application)
        db.session.commit()
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('apply.html', job=job, is_hot=False)


@app.route('/logout')
def logout():
    """Logs out the current user by clearing the session."""
    session.clear()
    return redirect(url_for('home'))


@app.route('/edit-job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    """Allows an employer to edit a job they posted."""
    if session['role'] != 'employer':
        return redirect(url_for('login'))
    job = Job.query.get_or_404(job_id)
    if job.employer_id != session['user_id']:
        return "❌ Unauthorized access", 403
    if request.method == 'POST':
        # Update job info from form submission
        job.title = request.form['title']
        job.description = request.form['description']
        job.salary = request.form['salary']
        job.location = request.form['location']
        job.company = request.form['company']
        db.session.commit()
        flash('Job updated successfully!', 'success')   # <-- Add this line
        return redirect(url_for('dashboard'))
    # Show form with current job data for editing
    return render_template('edit_job.html', job=job)


if __name__ == '__main__':
    # Create database tables if missing, then run development server
    with app.app_context():
        db.create_all()
    app.run(debug=True)
