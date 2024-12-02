from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Azeem%40123@localhost:3306/flask_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    mail_id = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)

# Define the Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    event_details = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    event_description = db.Column(db.Text, nullable=True)
    contact_details = db.Column(db.String(100), nullable=False)
    event_size = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('events', lazy=True))

# Initialize the database
with app.app_context():
    db.create_all()

# Routes for user authentication
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def registration():
    return render_template('registration.html')

@app.route('/register/submit', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    re_password = request.form['re_password']
    mobile_number = request.form['mobile_number']
    mail_id = request.form['mail_id']
    city = request.form['city']
    state = request.form['state']

    if not username or not password or not re_password or not mobile_number or not mail_id:
        flash("All fields are required!", "danger")
        return redirect(url_for('registration'))

    if password != re_password:
        flash("Passwords do not match!", "danger")
        return redirect(url_for('registration'))

    if User.query.filter_by(username=username).first():
        flash("Username already exists!", "danger")
        return redirect(url_for('registration'))

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, mobile_number=mobile_number,
                    mail_id=mail_id, city=city, state=state)
    db.session.add(new_user)
    db.session.commit()

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for('login'))

@app.route('/login/submit', methods=['POST'])
def login_submit():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        flash('Logged in successfully!', 'success')
        return redirect(url_for('events')) 
    else:
        flash('Invalid username or password!', 'danger')
        return redirect(url_for('login'))

# Routes for event management
@app.route('/events')
def events():
    if 'user_id' not in session:
        flash('Please log in to create or access your events.', 'danger')
        return redirect(url_for('login'))  # Redirect to login if not logged in
    events = Event.query.filter_by(user_id=session['user_id']).all()  # Fetch events related to the logged-in user
    return render_template('events.html', events=events)

@app.route('/events/new', methods=['GET', 'POST'])
def new_event():
    if 'user_id' not in session:
        flash('You need to log in to create an event!', 'danger')
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        try:
            start_datetime = datetime.strptime(request.form['start_datetime'], '%Y-%m-%dT%H:%M')
            end_datetime = datetime.strptime(request.form['end_datetime'], '%Y-%m-%dT%H:%M')

            # Check if start date is later than end date
            if start_datetime > end_datetime:
                flash('Start date cannot be greater than the end date!', 'danger')
                return redirect(url_for('new_event'))  # Stay on the event creation page
            event = Event(
                name=request.form['name'],
                location=request.form['location'],
                event_type=request.form['event_type'],
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                event_description=request.form['event_description'],
                contact_details=request.form['contact_details'],
                event_size=request.form['event_size'],
                user_id=session['user_id']  # Link the event to the logged-in user
            )
            db.session.add(event)
            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('login'))  # Redirect to events page after creating the event
        except Exception as e:
            flash(f'Error creating event: {e}', 'danger')
            return redirect(url_for('events'))  # Stay on the event creation page if an error occurs

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user_id from the session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))  # Redirect to the login page


# Other routes
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
