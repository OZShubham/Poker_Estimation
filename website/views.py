from flask import Blueprint, render_template,url_for,request,session,redirect,Flask,jsonify
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
        
        if not team_id or not user_role or not poker_board_type:
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
            'user_role' : user_role,
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
    if request.method == 'POST':
        if 'email' not in session:
            return redirect('/login')
        else:
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

    return render_template('team_view.html')


@views.route('/scrum_master_view', methods=['GET', 'POST'])
def scrum_master_view():
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
            jira_id = estimate.get('jira_id')
            users = estimate.get('users', [])
        for user in users:
            user_id = user.get('user_id')
            story_point = user.get('story_point')
            story_points.append({'user_id': user_id,'Jira-id': jira_id, 'Story point': story_point})

            
        
        if not estimate:
            return 'Error: No estimate found with given jira_id'
        
        # Render the retrieved data in scrum_master_view.html template
        #return render_template('scrum_master_view.html', estimate=estimate)
        return json.dumps(story_points)

    else:
        # Render the input form in form.html template
        return render_template('scrum_master_view.html')



@views.route('/t-shirt')
def tshirt():
    return render_template('t-shirt.html')

@views.route('/')
def home():
    return render_template('home.html')

    




