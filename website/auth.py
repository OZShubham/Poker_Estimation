
# Import required modules
from flask import Flask, render_template, request, Blueprint, url_for, redirect, session, flash
from google.cloud import datastore
import bcrypt
import os


# Create a Flask app
auth = Blueprint('auth', __name__)

# Initialize Datastore client
datastore_client = datastore.Client()


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data from request
        name = request.form['name']
        email = request.form['email']
        user_role = request.form['user_role']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        # Check if password and confirm password match
        if password != confirm_password:
            return 'Password and Confirm Password do not match', 400

        # Check if user already exists in Datastore
        query = datastore_client.query(kind='User')
        query.add_filter('email', '=', email)
        existing_users = query.fetch()

        if len(list(existing_users)) > 0:
            return 'User with this email already exists', 400

        # Hash the password

        # Save new user to Datastore
        user_key = datastore_client.key('User')
        user = datastore.Entity(key=user_key)
        user['name'] = name
        user['email'] = email
        user['user_role'] = user_role
        user['password'] = hashed_password.decode('utf-8')
        datastore_client.put(user)

        flash("Account Created Successfully!", "info")
        return redirect('/login')

    else:
        if "email" in session:
            flash("Already Logged In!", "info")
            return redirect('/scrum_team_member_view')

        # Render the signup page for GET request
        return render_template('signup.html')


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():

    
        if request.method == 'POST':
            email = request.form['email']
            new_password = request.form['new_password']

            # Check if email and new password are provided
            if not email or not new_password:
                return 'Email and new password are required', 400

            # Query Datastore to check if email exists
            query = datastore_client.query(kind='User')
            query.add_filter('email', '=', email)
            result = list(query.fetch())  # Convert query result to list

            # If a user with the given email is found
            if len(result) > 0:
                user = result[0]

                # Update user's password in Datastore
                user['password'] = new_password
                datastore_client.put(user)

                return redirect('/login')
            else:
                return 'Email not found', 404

   


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Retrieve user entity from Datastore based on email
            query = datastore_client.query(kind='User')
            query.add_filter('email', '=', email)
            result = list(query.fetch(limit=1))

            if result:
                user = result[0]
                # Retrieve hashed password from Datastore
                hashed_password = user['password'].encode('utf-8')

                # Verify input password with hashed password
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    # Passwords match, return success
                    response = {'success': True,
                                'message': 'Sign-in successful'}
                    flash("Logged In Successfully!", "info")
                    session["email"] = email  # creating session key
                    
                    if user['user_role'] == 'scrum_master':
                        return redirect('/scrum_master_landing')
                    else:
                        return redirect('/scrum_member_landing')

                else:
                    # Passwords don't match, return error
                    flash("Incorrect Password!", "info")
                    return redirect('/login')
            else:
                # User not found, return error
                flash("Incorrect Email!", "info")
                return redirect('/login')
        except Exception as e:
            print('Error:', e)
            # Return error response
            response = {'success': False, 'message': 'An error occurred'}

        return response
    # Render the login page for GET request
    else:
        if "email" in session:
            flash("Already Logged In!", "info")
            return redirect('/scrum_team_member_view')

        return render_template('login.html')


@auth.route('/logout')
def logout():
    # Logout logic here
    session.clear()
    flash("You have been logged out!", "info")
    return redirect('/login')
