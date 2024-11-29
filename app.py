from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Azeem%40123@localhost:3306/flask_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Required for session management and flashing messages

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

# Initialize the database
with app.app_context():
    db.create_all()

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
        return "All fields are required!", 400

    if password != re_password:
        return "Passwords do not match!", 400

    # Check if the username already exists
    if User.query.filter_by(username=username).first():
        return "Username already exists!", 400

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    # Save the user to the database
    new_user = User(username=username, password=hashed_password, mobile_number=mobile_number,
                    mail_id=mail_id, city=city, state=state)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/login/submit', methods=['POST'])
def login_submit():
    username = request.form['username']
    password = request.form['password']

    # Check if the username exists
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        # Store user ID in the session after successful login
        session['user_id'] = user.id
        return redirect(url_for('events'))  # Redirect to events page if login is successful
    else:
        flash('Invalid username or password!', 'danger')
        return redirect(url_for('login'))  # Redirect back to login page on failure

@app.route('/events')
def events():
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if the user is not logged in
    return render_template('events.html')


@app.route('/home')
def home():
    return render_template('index.html')  # Assuming 'index.html' is the homepage

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/events')
def events_page():
    return render_template('events.html')

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
