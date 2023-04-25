from flask import Blueprint, render_template,url_for,request,session,redirect,Flask,jsonify,flash
from google.cloud import datastore
import json
import datetime
import hashlib

import random
import string
from google.cloud import datastore


views = Blueprint('views', __name__)







@views.route('/create_poker_board')
def go_to_board():
    
    if 'email' not in session:
        return redirect('/login')
    return render_template('create_board.html')

@views.route('/create_poker_board', methods=['GET','POST'])
def create_poker_board():
    if request.method == 'POST':
        if 'email' not in session:
            return redirect('/login')
        else:
            email = session['email']
            team_id = request.form.get('team_id')
            user_role = request.form.get('user_role')
            poker_board_type = request.form.get('poker_board_type')
        
        if not team_id or not poker_board_type:
            return jsonify({'error': 'Bad Request. Required fields are missing in the request body.'}), 400
        
        '''def create_board_id(user_id):
            current_time = datetime.datetime.now().strftime("%d%m%y")
            board_id_str = "poker_board" + user_id + current_time
            hash_value = hashlib.md5(board_id_str.encode('utf-8')).hexdigest()
            return hash_value'''
        def create_board_id(user_id):
            current_time = datetime.datetime.now().strftime("%d%m%y")
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Generate a random string of length 8
            board_id_str =  user_id + current_time + random_string
            hash_value = hashlib.md5(board_id_str.encode('utf-8')).hexdigest()
            return hash_value
        
        poker_board_id = create_board_id(email)
        
        response_dict = {
            'user_id' : email,
            'poker_board_id': poker_board_id,
            'poker_board_type': poker_board_type,
            'org_id': 'cognizant',
            'created_timestamp': datetime.datetime.utcnow(),
            'last_modified_timestamp': datetime.datetime.utcnow(),
            'team_id': team_id,
            'status' : 'Created'
        }

        # Save response_dict to Datastore
        client = datastore.Client()
        entity_key = client.key('PokerBoard', poker_board_id)
        entity = datastore.Entity(key=entity_key)
        entity.update(response_dict)
        client.put(entity)

        return redirect(url_for('views.scrum_team_member_view')) 
    
    # Return a default response for other request methods
    return jsonify({'error': 'Method not allowed'}), 405



'''@views.route('/scrum_master_view')
def go_to_scrum_master_view():
    return render_template('scrum_master_view.html')'''


'''@views.route('/scrum_team_member_view')
def scrum_team_member_view():
    return render_template('team_view.html')'''



@views.route('/scrum_team_member_view', methods=['GET', 'POST'])
def scrum_team_member_view():
    if 'email' not in session:
        return redirect('/login')

    if request.method == 'POST':
        poker_board_id = request.form.get('poker_board_id')
        jira_id = request.form.get('jira_id')
        user_id = request.form.get('user_id')
        story_point = request.form.get('story_point')

        # Retrieve email from session
        email = session.get('email')

        # Validate input data
        if not poker_board_id or not jira_id or not user_id:
            return 'Error: Missing required data in the request', 400

        # Query Datastore for user with matching email
        client = datastore.Client()
        query = client.query(kind='User')
        query.add_filter('email', '=', email)
        result = list(query.fetch(limit=1))
        if not result:
            return 'Error: User not found', 404

        # Update PokerBoard entity
        entity_key = client.key('PokerBoard', poker_board_id)
        entity = client.get(entity_key)
        if not entity:
            return 'Error: No entity found with poker_board_id {}'.format(poker_board_id), 404

        jira_id = request.form.get('jira_id')
        user_id = request.form.get('user_id')
        story_point = request.form.get('story_point')
        updated_estimate = False
        updated_user = False
        estimates = entity.get('estimates', [])

        for estimate in estimates:
            if estimate.get('jira_id') == jira_id:
                users = estimate.get('users', [])
                for user in users:
                    if user.get('user_id') == user_id:
                        user['story_point'] = story_point
                        user['created_timestamp'] = datetime.datetime.utcnow()
                        updated_user = True
                        updated_estimate = True
                        break

                if not updated_user:
                    users.append({'user_id': user_id, 'story_point': story_point,
                                  'created_timestamp': datetime.datetime.utcnow()})
                    estimate['users'] = users
                    updated_estimate = True
                break

        if not updated_estimate:
            estimates.append({'jira_id': jira_id, 'users': [{'user_id': user_id, 'story_point': story_point,
                                                              'created_timestamp': datetime.datetime.utcnow()}]})

        entity.update({'estimates': estimates, 'last_modified_timestamp': datetime.datetime.utcnow()})
        client.put(entity)

        return json.dumps(entity, default=str)

    return render_template('scrum_team_member_view.html')



@views.route('/scrum_master_view', methods=['GET', 'POST'])
def scrum_master_view():
    if 'email' not in session:
        return redirect('/login')
    if request.method == 'POST':
        poker_board_id = request.form.get('poker_board_id')
        jira_id = request.form.get('jira_id')
        
        if not poker_board_id or not jira_id:
            return 'Error: poker_board_id or jira_id field not provided in request.'
        
        client = datastore.Client()
        entity_key = client.key('PokerBoard', poker_board_id)
        entity = client.get(entity_key)
        
        if not entity:
            return 'Error: No entity found with given poker_board_id'
        
        estimates = entity.get('estimates', [])
        story_points = []
        for estimate in estimates:
            if estimate.get('jira_id') == jira_id:
                users = estimate.get('users', [])
                for user in users:
                    user_id = user.get('user_id')
                    story_point = user.get('story_point')
                    story_points.append({'user_id': user_id,  'Story point': story_point})

        if not story_points:
            return 'Error: No estimate found with given jira_id'
        
        # Render the retrieved data in scrum_master_view.html template
        # return render_template('scrum_master_view.html', estimate=estimate)
        return render_template('estimates.html', story_points=story_points)

    else:
        # Render the input form in form.html template
        return render_template('scrum_master_view.html')



'''@views.route('/t-shirt')
def tshirt():
    return render_template('t-shirt.html')'''

@views.route('/')
def home():
    return render_template('home.html')



datastore_client = datastore.Client()
@views.route('/scrum_master_landing')
def all_boards():
    query = datastore_client.query(kind='PokerBoard')
    boards = query.fetch()

    return render_template('scrum_master_landing.html', boards=boards)   


from flask import jsonify, request
from flask.views import MethodView
from google.cloud import datastore

# Create a Datastore client
datastore_client = datastore.Client()

@views.route('/grant_user_access', methods=['GET', 'POST'])
def grant_user_access():
    if 'email' not in session:
        return redirect('/login')
    datastore_client = datastore.Client()
    if request.method == 'POST':
        # Get data from form
        poker_board_id = request.form.get('poker_board_id')
        query = datastore_client.query(kind='PokerBoard')
        boards = query.fetch()
        # Retrieve email from session
        email = session.get('email')

        # Query Datastore for user with matching email
        
        query = datastore_client.query(kind='User')
        query.add_filter('email', '=', email)
        result = list(query.fetch(limit=1))
        if not result:
            return 'Error: User not found', 404
        user = result[0]
        
        # Check if user has Scrum Master role
        if user['email'] != email:
            return 'Error: chal gya', 401

        # Get PokerBoard entity from Datastore
        poker_board_key = datastore_client.key('PokerBoard', poker_board_id)
        poker_board = datastore_client.get(poker_board_key)

        # Check if PokerBoard entity exists
        if not poker_board:
            return jsonify({'error': 'Poker Board does not exist'}), 404

        # Get User entity from Datastore
        user_id = request.form.get('user_id')
        user_key = datastore_client.key('User', int(user_id))
        user = datastore_client.get(user_key)

        # Check if User entity exists
        if not user:
            return jsonify({'error': 'User does not exist'}), 404

        # Grant access to user by adding poker_board_id to User's list of entitlement
        user['entitlement'] = []
        user['entitlement'].append(poker_board_id)
        datastore_client.put(user)

        flash(f'Access granted to user {user["name"]} for Poker Board {poker_board_id}', 'success')
        return redirect('/grant_user_access')

    # Render the HTML page for GET requests
    users_query = datastore_client.query(kind='User')
    users = list(users_query.fetch())
    return render_template('grant_user_access.html', users=users)


@views.route('/poker_master_landing')
def poker_master_landing():
    return render_template('poker_master_landing.html')


@views.route('/create_jira_id')
def create_jira_id():
    return render_template('create_jira_id.html')

@views.route('/choose_jira_id', methods = ['GET','POST'])
def choose_jira_id():
    if request.method == "POST":
        return redirect('/scrum_master_view')
    
    else:
        return render_template('choose_jira_id.html')
    

@views.route('/scrum_member_landing', methods = ['GET','POST'])
def scrum_member_landing():
    if request.method == "POST":
        return redirect('/choose_jiraa_id')
    
    else:
        return render_template('scrum_member_landing.html')    
    

@views.route('/choose_jiraa_id', methods = ['GET','POST'])
def choose_jiraa_id():
    if request.method == "POST":
        return redirect('/scrum_team_member_view')
    
    else:
        return render_template('choose_jiraa_id.html')  


 


@views.route('/t_shirt', methods=['GET', 'POST'])
def  t_shirt():
    if 'email' not in session:
        return redirect('/login')

    if request.method == 'POST':
        poker_board_id = request.form.get('poker_board_id')
        jira_id = request.form.get('jira_id')
        user_id = request.form.get('user_id')
        story_point = request.form.get('story_point')
       
        # Retrieve email from session
        email = session.get('email')

        # Validate input data
        if not poker_board_id or not jira_id or not user_id:
            return 'Error: Missing required data in the request', 400

        # Query Datastore for user with matching email
        client = datastore.Client()
        query = client.query(kind='User')
        query.add_filter('email', '=', email)
        result = list(query.fetch(limit=1))
        if not result:
            return 'Error: User not found', 404

        # Update PokerBoard entity
        entity_key = client.key('PokerBoard', poker_board_id)
        entity = client.get(entity_key)
        if not entity:
            return 'Error: No entity found with poker_board_id {}'.format(poker_board_id), 404

        jira_id = request.form.get('jira_id')
        user_id = request.form.get('user_id')
        story_point = request.form.get('story_point')
        updated_estimate = False
        updated_user = False
        estimates = entity.get('estimates', [])

        for estimate in estimates:
            if estimate.get('jira_id') == jira_id:
                users = estimate.get('users', [])
                for user in users:
                    if user.get('user_id') == user_id:
                        user['story_point'] = story_point
                        user['created_timestamp'] = datetime.datetime.utcnow()
                        updated_user = True
                        updated_estimate = True
                        break

                if not updated_user:
                    users.append({'user_id': user_id, 'story_point': story_point,
                                  'created_timestamp': datetime.datetime.utcnow()})
                    estimate['users'] = users
                    updated_estimate = True
                break

        if not updated_estimate:
            estimates.append({'jira_id': jira_id, 'users': [{'user_id': user_id, 'story_point': story_point,
                                                              'created_timestamp': datetime.datetime.utcnow()}]})

        entity.update({'estimates': estimates, 'last_modified_timestamp': datetime.datetime.utcnow()})
        client.put(entity)

        return json.dumps(entity, default=str)

    return render_template('t_shirt.html')
    
