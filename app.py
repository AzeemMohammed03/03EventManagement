from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Root route for login page
@app.route('/')
def login():
    return render_template('login.html')

# Route for registration page
@app.route('/register')
def registration():
    return render_template('registration.html')

# Registration form submission route
@app.route('/register/submit', methods=['POST'])
def register():
    # Retrieve form data
    username = request.form['username']
    password = request.form['password']
    re_password = request.form['re_password']
    mobile_number = request.form['mobile_number']
    mail_id = request.form['mail_id']
    city = request.form['city']
    state = request.form['state']

    # Validation checks
    if not username or not password or not re_password or not mobile_number or not mail_id:
        return "All fields are required!", 400

    if password != re_password:
        return "Passwords do not match!", 400

    # Redirect back to login after successful registration
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
