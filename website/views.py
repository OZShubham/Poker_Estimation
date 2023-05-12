from flask.views import MethodView
from flask import jsonify, request
from flask import Blueprint, render_template, url_for, request, session, redirect, Flask, jsonify, flash
from google.cloud import datastore
import json
import datetime
import hashlib
import random
import string
import os
from google.cloud import storage
from google.cloud import datastore


views = Blueprint('views', __name__)

def user_event(event):

    user_id = session.get('email')

    response = {
        'user_id' : user_id,
        'event_type' : event,
        'created_timestamp' : datetime.datetime.utcnow()
    }
    
    client = datastore.Client()
    entity_key = client.key('UserEvent')
    entity = datastore.Entity(key=entity_key)
    entity.update(response)
    client.put(entity)

    return

@views.route('/create_poker_board')
def go_to_board():

    if 'email' not in session:
        return redirect('/login')
    return render_template('create_board.html')


@views.route('/create_poker_board', methods=['GET', 'POST'])
def create_poker_board():
    if request.method == 'POST':
        if 'email' not in session:
            return redirect('/login')
        else:
            email = session['email']
            poker_board_name = request.form.get('poker_board_name')
            team_id = request.form.get('team_id')
            poker_board_type = request.form.get('poker_board_type')

        if not team_id or not poker_board_type:
            return jsonify({'error': 'Bad Request. Required fields are missing in the request body.'}), 400

        
        def create_board_id(user_id):
            current_time = datetime.datetime.now().strftime("%d%m%y")
            # Generate a random string of length 8
            random_string = ''.join(random.choices(
                string.ascii_letters + string.digits, k=8))
            board_id_str = user_id + current_time + random_string
            hash_value = hashlib.md5(board_id_str.encode('utf-8')).hexdigest()
            return hash_value

        poker_board_id = create_board_id(email)

        response_dict = {
            'user_id': email,
            'poker_board_name': poker_board_name,
            'poker_board_id': poker_board_id,
            'poker_board_type': poker_board_type,
            'org_id': 'cognizant',
            'created_timestamp': datetime.datetime.utcnow(),
            'last_modified_timestamp': datetime.datetime.utcnow(),
            'team_id': team_id,
            'status': 'Created'
        }

        # Save response_dict to Datastore
        client = datastore.Client()
        entity_key = client.key('PokerBoard', poker_board_id)
        entity = datastore.Entity(key=entity_key)
        entity.update(response_dict)
        client.put(entity)

        # Calling the function to log the event.
        event = 'created poker board'
        user_event(event)

        return redirect('/scrum_master_landing')

    # Return a default response for other request methods
    return jsonify({'error': 'Method not allowed'}), 405

@views.route('/create_jira_id',methods=['POST','GET'])
def create_jira_id():
    if request.method=='POST':
        poker_board_id = session.get('poker_board_id')
        print(poker_board_id)
        jira_id = request.form.get('jira_id')
        jira_description = request.form.get('jira_description')
        jira_title = request.form.get('jira_title')

        client = datastore.Client()

        entity_key = client.key('PokerBoard', poker_board_id)
        entity = client.get(entity_key)
        if not entity:
            return 'Error: No entity found with poker_board_id {}'.format(poker_board_id), 404
        estimates = entity.get('estimates', [])
        estimates.append({'jira_id': jira_id,'jira_description': jira_description,'jira_title' : jira_title})
        entity.update({'estimates': estimates,
                      'last_modified_timestamp': datetime.datetime.utcnow()})
        client.put(entity)

        event = 'created jira id'
        user_event(event)
        
        def create_new_story():
            poker_board_id = session.get('poker_board_id')
            print(poker_board_id)
            jira_id = request.form.get('jira_id')
            jira_description = request.form.get('jira_description')
            jira_title=request.form.get('jira_title')
            client = datastore.Client()
   
            entity_key = client.key('newStory',poker_board_id)
            entity = client.get(entity_key)
            if not entity:
                entity = datastore.Entity(key=entity_key)
            
            
            story= entity.get('story',[])
            story.append({'jira_id':jira_id,'jira_description': jira_description,'jira_title':jira_title,'created_timestamp': datetime.datetime.utcnow(),'last_modified_timestamp': datetime.datetime.utcnow()})
            entity.update({'story':story,'poker_board_id':poker_board_id})
            client.put(entity)

            return
        create_new_story()
        return redirect('/choose_jira_id')
    
    else:
        
        return render_template('create_jira_id.html')

@views.route('/upload', methods=['POST'])
def upload():
    poker_board_id = session.get('poker_board_id')
    file = request.files['file']
    if file:
        # Modify the filename to include the poker_board_id
        filename = f"{poker_board_id}_{file.filename}"
        # Upload the file to Google Cloud Storage
        client = storage.Client()
        bucket_name = 'poker-jira-bucket'  # Replace with your bucket name
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_file(file)

        flash('File uploaded successfully!', 'success')
        return redirect('/choose_jira_id')

    flash('No File is Selected.', 'danger')
    return redirect('/create_jira_id')


@views.route('/scrum_team_member_view', methods=['GET', 'POST'])
def scrum_team_member_view():

    event = 'on scrum team member view'
    user_event(event)

    poker_board_id = session.get('poker_board_id')
    jira_id = session.get('jira_id')
    name = session.get('name')
    
    if 'email' not in session:
        return redirect('/login')
    
    client = datastore.Client()
    entity_key = client.key('PokerBoard', poker_board_id)
    entity = client.get(entity_key)
    if not entity:
        return 'Error: No entity found with poker_board_id {}'.format(poker_board_id), 404
    
    estimates = entity.get('estimates', [])

    for estimate in estimates:
        if estimate.get('jira_id') == jira_id:
             jira_description = estimate.get('jira_description')
             jira_title = estimate.get('jira_title')

    if request.method == 'POST':
        
        user_id = session.get('email')
        
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

        
        user_id = session.get('email')
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
                        user['user_name'] = name
                        user['created_timestamp'] = datetime.datetime.utcnow()
                        updated_user = True
                        updated_estimate = True
                        break

                if not updated_user:
                    users.append({'user_id': user_id, 'user_name':name, 'story_point': story_point,
                                  'created_timestamp': datetime.datetime.utcnow()})
                    estimate['users'] = users
                    updated_estimate = True
                break

        if not updated_estimate:
            estimates.append({'jira_id': jira_id, 'users': [{'user_id': user_id,'user_name':name, 'story_point': story_point,
                                                             'created_timestamp': datetime.datetime.utcnow()}]})

        entity.update({'estimates': estimates,
                      'last_modified_timestamp': datetime.datetime.utcnow()})
        client.put(entity)

        return redirect('/choose_jiraa_id')

    return render_template('scrum_team_member_view.html',jira_description=jira_description,jira_id=jira_id,name=name,jira_title=jira_title)


@views.route('/poker_estimates', methods=['GET', 'POST'])
def poker_estimates():
    if 'email' not in session:
        return redirect('/login')
    else:

        event = 'on poker estimates'
        user_event(event)

        poker_board_id = session.get('poker_board_id')
        jira_id = session.get('jira_id')
        
        

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
                jira_title=estimate.get('jira_title')
                
                for user in users:
                    user_id = user.get('user_id')
                    user_name = user.get('user_name')
                    story_point = user.get('story_point')
                    story_points.append(
                        {'user_id': user_id, 'user_name':user_name,  'Story point': story_point})
                print(story_points)
        if not story_points:
            return render_template('no_vote.html')

        # Render the retrieved data in scrum_master_view.html template
        # return render_template('scrum_master_view.html', estimate=estimate)
        return render_template('estimates.html', story_points=story_points,jira_title=jira_title,jira_id=jira_id)

    





@views.route('/')
def home():

    #event = 'on home page'
    #user_event(event)

    return redirect('/login')


datastore_client = datastore.Client()


@views.route('/scrum_master_landing', methods=['GET', 'POST'])
def scrum_master_landing():

    if 'email' not in session:
        return redirect('/login')
    
    event = 'on scrum master landing'
    user_event(event)
    
    # Retrieve the user entity from Datastore based on the email in the session
    query = datastore_client.query(kind='User')
    query.add_filter('email', '=', session['email'])
    result = list(query.fetch(limit=1))

    if result:
        user = result[0]
        # Get the name of the logged in user
        name = user.get('name')
    else:
        # User not found, return error
        flash("Incorrect Email!", "info")
        return redirect('/login')

    query = datastore_client.query(kind='PokerBoard')
    boards = query.fetch()
    
    if request.method == 'POST':
        poker_board_id = request.form.get('poker_board_id')
        session['poker_board_id'] = poker_board_id
        return redirect('/choose_jira_id')
    else:
        return render_template('scrum_master_landing.html', name=name, boards=boards)

# Create a Datastore client
datastore_client = datastore.Client()


@views.route('/grant_user_access', methods=['GET', 'POST'])
def grant_user_access():
    if 'email' not in session:
        return redirect('/login')
    
    event = 'on grant user access'
    user_event(event)

    datastore_client = datastore.Client()
    query = datastore_client.query(kind='PokerBoard')
    boards = query.fetch()
    email = session.get('email')
    if request.method == 'POST':
        # Get data from form
        poker_board_id = request.form.get('poker_board_id')

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
            return 'Error', 401

        # Get PokerBoard entity from Datastore
        poker_board_key = datastore_client.key('PokerBoard', poker_board_id)
        poker_board = datastore_client.get(poker_board_key)
        poker_board_name = poker_board.get('poker_board_name')
        poker_board_type = poker_board.get('poker_board_type')

        # Check if PokerBoard entity exists
        if not poker_board:
            return jsonify({'error': 'Poker Board does not exist'}), 404

        # Get list of selected users from form
        user_ids = request.form.getlist('user_id')

        # Grant access to each selected user
        for user_id in user_ids:
            # Get User entity from Datastore
            user_key = datastore_client.key('User', user_id)
            user = datastore_client.get(user_key)

            # Check if User entity exists
            if not user:
                return jsonify({'error': 'User does not exist'}), 404

            # Grant access to user by adding poker_board_id to User's list of entitlement
            if 'entitlement' not in user:
                user['entitlement'] = []
            user['entitlement'].append({'poker_board_id': poker_board_id, 'poker_board_type':poker_board_type,  'poker_board_name': poker_board_name})
            datastore_client.put(user)

            flash(
                f'Access granted to user {user["name"]} for Poker Board {poker_board_name}', 'success')
        
        event = 'user access granted'
        user_event(event)

        return redirect('/grant_user_access')

    
    # Render the HTML page for GET requests
    users_query = datastore_client.query(kind='User')
    users_query.add_filter('email', '!=', email)
    users = list(users_query.fetch())
    return render_template('grant_user_access.html', users=users, boards=boards)




@views.route('/choose_jira_id', methods=['GET', 'POST'])
def choose_jira_id():
    poker_board_id = session.get('poker_board_id')
    client=datastore.Client()
    entity_key=client.key('newStory',poker_board_id)
    entity=client.get(entity_key)
    
    if not entity:
        flash(" There is no JIRA Title in your backlog, Please create JIRA Title.")
        return redirect('/create_jira_id')

    def get_backlog_story():
       

        backlog=entity.get('story',[])

        return json.dumps(backlog,indent=4, sort_keys=True, default=str)
        
    stories = get_backlog_story()
    stories_json = json.loads(stories)
    

    event = 'on choose jira id'
    user_event(event)

    # Extract the jira_ids from the fetched entities
    jira_ids = []
    for story in stories_json:
        jira_title = story.get('jira_title')

        jira_id = story.get('jira_id')
        if jira_id:
            jira_ids.append({'jira_id':jira_id,'jira_title':jira_title})

    if request.method == "POST":
        jira_id = request.form.get('jira_id')
        session['jira_id'] = jira_id
        print('jira_id:', jira_id)
        return redirect('/poker_estimates')

    else:
        return render_template('choose_jira_id.html', jira_ids=jira_ids)




@views.route('/scrum_member_landing', methods=['GET', 'POST'])
def scrum_member_landing():

    event = 'on scrum member landing'
    user_event(event)

    datastore_client = datastore.Client()
    email = session.get('email')

    # Retrieve the user's name from Datastore
    query = datastore_client.query(kind='User')
    query.add_filter('email', '=', email)
    result = list(query.fetch())
    name = result[0]['name'] if result else None #list comprehension
    session['name'] = name
    # Retrieve all entities of the User kind from Datastore
    query = datastore_client.query(kind='User')
    users = list(query.fetch())
    
    # Filter the list of users based on the email from the session
    users_with_matching_email = [user for user in users if user.get('email') == email]
    for user in users_with_matching_email:
        poker_boards = user.get('entitlement',[])

    
    if request.method == "POST":
        poker_board_id = request.form['poker_board_id']
        entity_key = datastore_client.key('PokerBoard', poker_board_id)
        entity = datastore_client.get(entity_key)
        poker_board_type = entity.get('poker_board_type')
        session['poker_board_id'] = poker_board_id
        session['poker_board_type'] = poker_board_type
        print(poker_board_type)

       
       
        return redirect(url_for('views.choose_jiraa_id',name=name))

    else:
        return render_template('scrum_member_landing.html', name=name, poker_boards=poker_boards, poker_board_id=session.get('poker_board_id'))



@views.route('/choose_jiraa_id', methods=['GET', 'POST'])
def choose_jiraa_id():
    
    def get_backlog_story():
        poker_board_id = session.get('poker_board_id')
        client=datastore.Client()
        entity_key=client.key('newStory',poker_board_id)
        entity=client.get(entity_key)
        backlog=entity.get('story',[])

        return json.dumps(backlog,indent=4, sort_keys=True, default=str)
        
    stories = get_backlog_story()
    stories_json = json.loads(stories)

    event = 'on choose jira id (scrum member)'
    user_event(event)

    # Extract the jira_ids from the fetched entities
    jira_ids = []
    for story in stories_json:
        jira_title = story.get('jira_title')
        jira_id = story.get('jira_id')
        if jira_id:
            jira_ids.append({'jira_id':jira_id,'jira_title':jira_title})

    if request.method == "POST":
        jira_id = request.form.get('jira_id')
        session['jira_id'] = jira_id
        poker_board_type =session.get('poker_board_type')
        if poker_board_type == 'Fibonacci Number':
            return redirect('/scrum_team_member_view')
        else:
            return redirect('/t_shirt')


    else:
        return render_template('choose_jiraa_id.html', jira_ids=jira_ids)





@views.route('/t_shirt', methods=['GET', 'POST'])
def t_shirt():

    event = 'on t-shirt view'
    user_event(event)

    poker_board_id = session.get('poker_board_id')
    jira_id = session.get('jira_id')
    name = session.get('name')
    
    if 'email' not in session:
        return redirect('/login')
    
    client = datastore.Client()
    entity_key = client.key('PokerBoard', poker_board_id)
    entity = client.get(entity_key)
    if not entity:
        return 'Error: No entity found with poker_board_id {}'.format(poker_board_id), 404
    
    estimates = entity.get('estimates', [])

    for estimate in estimates:
        if estimate.get('jira_id') == jira_id:
             jira_description = estimate.get('jira_description')
             jira_title =estimate.get('jira_title')

    if request.method == 'POST':
        
        user_id = session.get('email')
        
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

        
        user_id = session.get('email')
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
                        user['user_name'] = name
                        user['created_timestamp'] = datetime.datetime.utcnow()
                        updated_user = True
                        updated_estimate = True
                        break

                if not updated_user:
                    users.append({'user_id': user_id, 'user_name':name, 'story_point': story_point,
                                  'created_timestamp': datetime.datetime.utcnow()})
                    estimate['users'] = users
                    updated_estimate = True
                break

        if not updated_estimate:
            estimates.append({'jira_id': jira_id, 'users': [{'user_id': user_id,'user_name':name, 'story_point': story_point,
                                                             'created_timestamp': datetime.datetime.utcnow()}]})

        entity.update({'estimates': estimates,
                      'last_modified_timestamp': datetime.datetime.utcnow()})
        client.put(entity)

        return redirect('/choose_jiraa_id')

    return render_template('t_shirt.html',jira_description=jira_description,jira_id=jira_id,name=name,jira_title=jira_title)


