from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Azeem%40123@localhost:3306/flask_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    mail_id = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)

# Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    event_description = db.Column(db.Text, nullable=True)
    contact_details = db.Column(db.String(100), nullable=False)
    event_size = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('events', lazy=True))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    num_people = db.Column(db.Integer, nullable=False)
    hall_type = db.Column(db.String(50), nullable=False)
    food_type = db.Column(db.String(50), nullable=False)
    food_menu = db.Column(db.String(50), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    event = db.relationship('Event', backref=db.backref('bookings', lazy=True))

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)
    screenshot = db.Column(db.String(100), nullable=True)
    booking = db.relationship('Booking', backref=db.backref('payments', lazy=True))


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

@app.route('/events')
def events():
    if 'user_id' not in session:
        flash('Please log in to create or access your events.', 'danger')
        return redirect(url_for('login'))
    events = Event.query.filter_by(user_id=session['user_id']).all()
    return render_template('events.html', events=events)

@app.route('/events/new', methods=['GET', 'POST'])
def new_event():
    if 'user_id' not in session:
        flash('You need to log in to create an event!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        start_datetime = datetime.strptime(request.form['start_datetime'], '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(request.form['end_datetime'], '%Y-%m-%dT%H:%M')

        if start_datetime > end_datetime:
            flash('Start date cannot be greater than the end date!', 'danger')
            return redirect(url_for('new_event'))

        event = Event(
            name=request.form['name'],
            location=request.form['location'],
            event_type=request.form['event_type'],
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            event_description=request.form['event_description'],
            contact_details=request.form['contact_details'],
            event_size=request.form['event_size'],
            user_id=session['user_id']
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('bookings', event_id=event.id))  # Redirecting with event_id

    return render_template('new_event.html')

@app.route('/bookings/<int:event_id>', methods=['GET', 'POST'])
def bookings(event_id):
    event = Event.query.get_or_404(event_id)  # Fetch event details
    if request.method == 'POST':
        num_people = int(request.form['num_people'])
        hall_type = request.form['hall_type']
        food_type = request.form['food_type']
        food_menu = request.form['food_menu']

        # Food and hall pricing
        food_prices = {"basic": 180, "standard": 230, "premium": 300}
        extra = 200 if food_type == "non-veg" else 0
        hall_cost = 10000 if hall_type == "ac" else 7000

        total_food_cost = (food_prices[food_menu] + extra) * num_people
        total_cost = total_food_cost + hall_cost

        # Create a booking record
        booking = Booking(event_id=event_id, num_people=num_people, hall_type=hall_type,
                          food_type=food_type, food_menu=food_menu, total_cost=total_cost)
        db.session.add(booking)
        db.session.commit()

        flash("Booking confirmed!", "success")
        session['booking_id'] = booking.id  # Store booking ID in session
        return redirect(url_for('summary'))  # Assuming you have a 'summary' route

    return render_template('bookings.html', event=event)

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    if 'booking_id' not in session:
        flash("No booking found.", "danger")
        return redirect(url_for('bookings'))

    booking = Booking.query.get(session['booking_id'])
    
    # Fetch the event associated with this booking
    event = Event.query.get(booking.event_id)

    if request.method == 'POST':
        payment_type = request.form.get('payment_type')
        screenshot = request.files.get('screenshot')

        if payment_type == 'online' and not screenshot:
            flash("Please upload a screenshot for online payment.")
            return redirect(url_for('summary'))

        # Save the screenshot if uploaded
        if screenshot:
            filename = screenshot.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            screenshot.save(filepath)

        # Create payment record
        payment = Payment(booking_id=booking.id, payment_type=payment_type, 
                          screenshot=filepath if screenshot else None)
        db.session.add(payment)
        db.session.commit()

        flash(f"Payment type selected: {payment_type}", "success")
        return redirect(url_for('summary'))

    # Display summary data, now include 'event' for rendering the event details
    return render_template('summary.html', 
                           event=event,  # Pass the event object to the template
                           num_people=booking.num_people,
                           food_type=booking.food_type,
                           food_cost=booking.total_cost - 10000,  # Assuming hall cost is fixed
                           hall_cost=10000 if booking.hall_type == "ac" else 7000,
                           total_cost=booking.total_cost)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
