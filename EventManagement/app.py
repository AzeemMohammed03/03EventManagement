from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Home page route
@app.route('/')
def home():
    return render_template('registration.html')

# Registration form route
@app.route('/register', methods=['POST'])
def register():
    # Retrieve form data
    username = request.form['username']
    password = request.form['password']
    re_password = request.form['re_password']
    mobile_number = request.form['mobile_number']
    mail_id = request.form['mail_id']
    city = request.form['city']
    state = request.form['state']

    # Validate form data
    if not username or not password or not re_password or not mobile_number or not mail_id:
        return "All fields are required!", 400  # Bad Request (validation failed)

    if password != re_password:
        return "Passwords do not match!", 400  # Validation error for password mismatch

    # You can add more validation here (e.g., check if mobile number is valid, etc.)

    # If validation passes, you can save the data or process further
    # For now, just redirect to a success page (or you can return a success message)
    return redirect(url_for('success'))

# Success page route
@app.route('/success')
def success():
    return "Registration successful!"

if __name__ == '__main__':
    app.run(debug=True)