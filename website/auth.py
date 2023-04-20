'''from flask import Flask, render_template,Blueprint, request, redirect,url_for
from google.cloud import datastore

auth = Blueprint('auth', __name__)




@auth.route('/login')
def login():
    return render_template('login.html')



@auth.route('/signup' )
def signup():
    return render_template('signup.html')
'''

# Import required modules
from flask import Flask, render_template, request, Blueprint, url_for, redirect, session ,jsonify,flash
from google.cloud import datastore
import bcrypt



# Create a Flask app
auth = Blueprint('auth', __name__)

# Initialize Datastore client
datastore_client = datastore.Client()

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Check if password and confirm password match
        if password != confirm_password:
            flash('Password and Confirm Password do not match', 'error')
            return redirect(url_for('auth.signup'))  # Redirect back to signup page

        # Check if user already exists in Datastore
        query = datastore_client.query(kind='User')
        query.add_filter('email', '=', email)
        existing_users = query.fetch()

        if len(list(existing_users)) > 0:
            flash('User with this email already exists', 'error')
            return redirect(url_for('auth.signup'))  # Redirect back to signup page

        # Hash the password

        # Save new user to Datastore
        user_key = datastore_client.key('User')
        user = datastore.Entity(key=user_key)
        user['name'] = name
        user['email'] = email
        user['password'] = hashed_password.decode('utf-8')
        datastore_client.put(user)

        flash('Signup successful', 'success')
        return redirect(url_for('auth.login'))  # Redirect to login page after successful signup

    # Render the signup page for GET request
    return render_template('signup.html')


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():

    if request.method == 'POST':
      email = request.form['email']
      new_password = request.form['new_password']
      result,status_code = reset_password(email,new_password)

      if status_code == 200:
            # Handle form submission success
            return redirect(url_for('auth.login'))  # Update with the appropriate route or URL for create_poker_board()
      else:
            # Handle form submission error
            return render_template('auth.login', error=result)

    return render_template('reset_password.html')




@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data from request
        email = request.form['email']
        password = request.form['password']
        session["email"] = email

        # Query Datastore for user with matching email
        query = datastore_client.query(kind='User')
        query.add_filter('email', '=', email)
        result = list(query.fetch(limit=1))

        if result:
            user = result[0]
            # Retrieve hashed password from Datastore
            hashed_password = user['password'].encode('utf-8')

            # Verify input password with hashed password
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                # Passwords match, set email as user ID in session
                session['email'] = email
                flash('Login successful', 'success')
                return redirect(url_for('views.go_to_board'))  # Redirect to create_poker_board after successful login
            else:
                flash('Incorrect email or password', 'error')
                return redirect(url_for('auth.login'))  # Redirect back to login page for incorrect password

        else:
            flash('Incorrect email or password', 'error')
            return redirect(url_for('auth.login'))  # Redirect back to login page for incorrect email

    # Render login page for GET requests
    return render_template('login.html')




@auth.route('/logout')
def logout():
    session.clear()
    # Logout logic here
    return redirect(url_for('auth.login'))








