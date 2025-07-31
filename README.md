# **Job Portal Web Application**

A full-stack job portal platform built with Flask, SQLAlchemy, and styled with Bootstrap and custom CSS. This project enables employers to post jobs, jobseekers to apply, and admins to manage users and jobs seamlessly.


## **Table of Contents**

- **Features**  
- **Tech Stack**  
- **Project Structure**  
- **Setup & Installation**  
- **Usage**  
- **Routes & Functionality**  
- **Responsive Design**  
- **Contributing**  

## **Features**

- **User Roles:** Supports jobseeker, employer, and admin roles with differentiated access.  
- **User Authentication:** Registration, login, and session management with secure password hashing.  
- **Job Posting:** Employers can post, edit, and delete jobs.  
- **Job Application:** Jobseekers can apply to jobs (including demo ‘hot jobs’).  
- **Dashboard:** Role-specific dashboards displaying jobs posted or applied to, and admin controls.  
- **Hot Jobs Data:** Includes a curated set of popular jobs (hot jobs) with detailed info.  
- **Search Functionality:** Search jobs by title, company, or location on the homepage.  
- **Responsive UI:** Mobile, tablet, and desktop friendly UI using Bootstrap and custom CSS.  
- **Flash Messages:** Inform users about actions like login errors, job updates, applications, etc.  
- **Secure Route Protection:** Decorator to restrict access to authenticated users only.  
- **Database:** Persistent storage with SQLite and SQLAlchemy ORM.  


## **Tech Stack**

- **Backend:** Python, Flask, SQLAlchemy ORM  
- **Database:** SQLite  
- **Frontend:** HTML, Bootstrap 5, custom CSS  
- **Security:** Werkzeug for password hashing  
- **Template Engine:** Jinja2 (Flask default)  


## **Project Structure**

jobportal/
│
├── app.py # Flask application entry point
── instance/ 
│ ├── jobportal.db # SQLite database file (auto-generated)
├── templates/ # Jinja2 HTML templates
│ ├── base.html
│ ├── home.html
│ ├── login.html
│ ├── register.html
│ ├── dashboard.html
│ ├── post_job.html
│ ├── edit_job.html
│ ├── apply.html
│ └── jobs.html
├── static/
│ ├── css/
│ │ └── styles.css # Custom CSS with responsive design
│ ├── assets/
│ │ └── images # Static images if any
├── README.md # This file
└── requirements.txt # Python dependencies list

## **Setup & Installation**

1. **Clone the repository:**
git clone https://github.com/yourusername/jobportal.git
cd jobportal

2. **Create a virtual environment (recommended):**
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

3. **Install dependencies:**
pip install -r requirements.txt

4. **Initialize the database:**
python app.py

The database (`jobportal.db`) and necessary tables will be created automatically on first run.

5. **Run the development server:**

flask run
or
python app.py

Visit http://127.0.0.1:5000/ in your browser to use the app.

## **Usage**

- **Register an account:** Choose role as jobseeker or employer (admin can be seeded manually).  
- **Employers:** Post jobs, edit or delete your job listings via the dashboard.  
- **Jobseekers:** Search and apply to jobs, view your applications in the dashboard.  
- **Admins:** Manage all users and jobs on a unified dashboard.  
- **Apply to Demo 'Hot Jobs':** Apply to preset hot jobs for demonstration.  
- **Logout:** Clear session and return to homepage.  


## **Routes & Functionality**

| Route              | Methods     | Description                               | Access           |
|--------------------|-------------|-------------------------------------------|------------------|
| `/`                | GET         | Home page, job listings + search           | Public           |
| `/about`           | GET         | About page                               | Public           |
| `/register`        | GET, POST   | User registration                        | Public           |
| `/login`           | GET, POST   | User login                              | Public           |
| `/logout`          | GET         | Logout user                            | Logged-in users  |
| `/dashboard`       | GET         | Role-specific dashboard                  | Logged-in users  |
| `/post-job`        | GET, POST   | Post a new job (employers only)             | Employer         |
| `/edit-job/<id>`   | GET, POST   | Edit existing job (employers only)           | Employer         |
| `/delete-job/<id>` | POST        | Delete a job (employers only)                 | Employer         |
| `/apply/<id>`      | GET, POST   | Apply to a job (jobseekers only)               | Jobseeker/Public |  

> _Note:_ Hot jobs have IDs like `"hot-<num>"` handled specially.


## **Responsive Design**

- The UI adjusts gracefully across desktop, tablet, and mobile screen sizes.  
- Uses Bootstrap 5 for grid and components.  
- Custom CSS provides smooth animations, gradients, and enhanced usability.  
- Media queries ensure fonts, buttons, and layouts remain accessible on small devices.  


## **Contributing**

Contributions are welcome! Feel free to:

- Improve UI/UX or accessibility  
- Add unit tests or integration tests  
- Implement additional features (notifications, resume uploads, etc.)  
- Fix bugs or improve code structure  

Please fork the repo and submit pull requests.
