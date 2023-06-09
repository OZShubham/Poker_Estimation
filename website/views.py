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

def get_user_name(user_id):
    client = datastore.Client()
    entity_key = client.key('User', user_id)
    entity = client.get(entity_key)
    user_name = entity.get('name')
    return user_name


def generate_signed_url(bucket_name, file_name, expiration_minutes=60):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=expiration_minutes)
    url = blob.generate_signed_url(expiration=expiration_time)

    return url

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
    if 'email' not in session:
        return redirect('/login')
    
    else:
        bucket_name = "url_template_poker"   #change the value according to your project
        file_name = "template.xlsx"             #change the value according to your project
        signed_url = generate_signed_url(bucket_name,file_name)

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
        
            return render_template('create_jira_id.html', signed_url=signed_url)

@views.route('/upload', methods=['POST'])
def upload():
    if 'email' not in session:
        return redirect('/login')
    else:
        poker_board_id = session.get('poker_board_id')
        file = request.files['file']
        if file:
            # Modify the filename to include the poker_board_id
            filename = f"{poker_board_id}_{file.filename}"
            # Upload the file to Google Cloud Storage
            client = storage.Client()
            bucket_name = 'initial_receiver'  # Replace with your bucket name
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
            
            poker_board_entitlements = user.get('entitlement', [])
            poker_board_exists = any(
                entitlement.get('poker_board_id') == poker_board_id for entitlement in poker_board_entitlements
            )
            if poker_board_exists:
                flash(f'User {user["name"]} already has access to Poker Board {poker_board_name}', 'danger')
                continue  # Skip granting access to this user

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
    if 'email' not in session:
        return redirect('/login')
    else:
        poker_board_id = session.get('poker_board_id')
        client=datastore.Client()
        entity_key=client.key('newStory',poker_board_id)
        entity=client.get(entity_key)
        
        if not entity:
            flash(" There is no JIRA Title in your backlog, Please create JIRA Title.", "danger")
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
    if 'email' not in session:
        return redirect('/login')
    else:

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
            if not poker_boards:  # Check if the list is empty
                return render_template('no_board.html', name=name)  # Render a template with a message
            else:
                return render_template('scrum_member_landing.html', name=name, poker_boards=poker_boards, poker_board_id=session.get('poker_board_id'))



@views.route('/choose_jiraa_id', methods=['GET', 'POST'])
def choose_jiraa_id():
    
    def get_backlog_story():
        poker_board_id = session.get('poker_board_id')
        client = datastore.Client()
        entity_key = client.key('newStory', poker_board_id)
        entity = client.get(entity_key)

        if entity is None or 'story' not in entity:
            return json.dumps([], indent=4, sort_keys=True, default=str)
        else:
            backlog = entity['story']
            return json.dumps(backlog, indent=4, sort_keys=True, default=str)


    if 'email' not in session:
        return redirect('/login')
    else:    
        stories = get_backlog_story()
        stories_json = json.loads(stories)

        if not stories_json:
            return render_template('no_jira.html')

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



# retrospective 



@views.route('/create_retro_board')
def go_to_retro_board():

    if 'email' not in session:
        return redirect('/login')
    query=datastore_client.query(kind='PokerBoard')
    boards=query.fetch()
    return render_template('create_retro_board.html',boards=boards)


@views.route('/create_retro_board', methods=['GET', 'POST'])
def create_retro_board():
    if request.method == 'POST':
        if 'email' not in session:
            return redirect('/login')
        else:
            
            email = session['email']
            retro_board_name = request.form.get('retro_board_name')
            team_id = request.form.get('team_id')
            poker_board_id = request.form.get('poker_board_id')

        if not poker_board_id:
            return jsonify({'error': 'Please Provide team_id and poker_board_id fields '}), 400

        def create_retro_board_id(user_id):
            current_time = datetime.datetime.now().strftime("%d%m%y")
            # Generate a random string of length 8
            random_string = ''.join(random.choices(
                string.ascii_letters + string.digits, k=8))
            board_id_str = user_id + current_time + random_string
            hash_value = hashlib.md5(board_id_str.encode('utf-8')).hexdigest()
            return hash_value

        retro_board_id = create_retro_board_id(email)
        client = datastore.Client()  
        # Query the PokerBoard entity to get the poker board name
        pokerboard_key = client.key('PokerBoard', poker_board_id)
        pokerboard_entity = client.get(pokerboard_key)

        if pokerboard_entity is not None:
            poker_board_name = pokerboard_entity.get('poker_board_name')
        else:
            poker_board_name = None




        response_dict = {
            'user_id': email,
            'retro_board_name': retro_board_name,
            'retro_board_id': retro_board_id,
            'team_id': team_id,
            'poker_board_name' : poker_board_name,
            'poker_board_id ':poker_board_id ,
            'org_id': 'cognizant',
            'created_timestamp': datetime.datetime.utcnow(),
            
            
            'status': 'Created'
        }

        # Save response_dict to Datastore
        client = datastore.Client()
        entity_key = client.key('RetroBoard',retro_board_id)
        entity = datastore.Entity(key=entity_key)
        entity.update(response_dict)
        client.put(entity)

        # Calling the function to log the event.
        event = 'Created Retrospective board'
        user_event(event)

        session['retro_board_id'] = retro_board_id

        return redirect('/choose_retro_board_master')


    # Return a default response for other request methods
    return jsonify({'error': 'Method not allowed'}), 405 







@views.route('/scrum_team_retro_view', methods=['GET', 'POST'])
def scrum_team_retro_view():

    event = 'on scrum team retro view'
    user_event(event)

    retro_board_id = session.get('retro_board_id')

    if 'email' not in session:
        return redirect('/login')

    client = datastore.Client()
    
    entity_key = client.key('RetroBoard', retro_board_id)
    entity = client.get(entity_key)
    if not entity:
        return 'Error: No entity found with retro_board_id {}'.format(retro_board_id), 404

    if request.method == 'POST':
        user_id = session.get('email')

        what_went_well = request.form['what_went_well']
        what_went_wrong = request.form['what_went_wrong']
        what_can_be_improved = request.form['what_can_be_improved']

        # Check if the PokerBoard entity has a 'users' property
        if 'users' not in entity:
            entity['users'] = []

        # Find the user's data dictionary or create a new one
        user_data = next((data for data in entity['users'] if user_id in data), {})
        user_data[user_id] = {
            'what_went_well': what_went_well,
            'what_went_wrong': what_went_wrong,
            'what_can_be_improved': what_can_be_improved
        }

        # Update the user's data in the PokerBoard entity
        if user_data not in entity['users']:
            entity['users'].append(user_data)

        client.put(entity)
        return redirect('/retro_results_team')

    return render_template('scrum_team_retro_view.html')

@views.route('/retro_results_master', methods=['GET'])
def retro_results_master():

    event = 'on retrospective results'
    user_event(event)

    retro_board_id = session.get('retro_board_id')

    if 'email' not in session:
        return redirect('/login')

    client = datastore.Client()
    entity_key = client.key('RetroBoard', retro_board_id)
    entity = client.get(entity_key)
    if not entity:
        return 'Error: No entity found with poker_board_id {}'.format(retro_board_id), 404

    user_retrospectives = []

    # Iterate over the users' data and retrieve the retrospective items
    for user_data in entity.get('users', []):
        for user_id, retrospective in user_data.items():
            user_name = get_user_name(user_id)  # Replace with your logic to get the user's name
            what_went_well = retrospective.get('what_went_well', '').split('~')
            what_went_wrong = retrospective.get('what_went_wrong', '').split('~')
            what_can_be_improved = retrospective.get('what_can_be_improved', '').split('~')

            user_retrospectives.append({
                'user_name': user_name,
                'what_went_well': what_went_well,
                'what_went_wrong': what_went_wrong,
                'what_can_be_improved': what_can_be_improved
            })

    if not user_retrospectives:
        return render_template('no_retro_result.html')
    else:
        return render_template('retro_results_master.html', user_retrospectives=user_retrospectives)
    


    
@views.route('/retro_results_team', methods=['GET'])
def retro_results_team():

    event = 'on retrospective results'
    user_event(event)

    retro_board_id = session.get('retro_board_id')

    if 'email' not in session:
        return redirect('/login')

    client = datastore.Client()
    entity_key = client.key('RetroBoard', retro_board_id)
    entity = client.get(entity_key)
    if not entity:
        return 'Error: No entity found with poker_board_id {}'.format(retro_board_id), 404

    user_retrospectives = []

    # Iterate over the users' data and retrieve the retrospective items
    for user_data in entity.get('users', []):
        for user_id, retrospective in user_data.items():
            user_name = get_user_name(user_id)  # Replace with your logic to get the user's name
            what_went_well = retrospective.get('what_went_well', '').split('~')
            what_went_wrong = retrospective.get('what_went_wrong', '').split('~')
            what_can_be_improved = retrospective.get('what_can_be_improved', '').split('~')

            user_retrospectives.append({
                'user_name': user_name,
                'what_went_well': what_went_well,
                'what_went_wrong': what_went_wrong,
                'what_can_be_improved': what_can_be_improved
            })

    if not user_retrospectives:
        return render_template('no_retro_result.html')
    else:
        return render_template('retro_results_team.html', user_retrospectives=user_retrospectives)



@views.route('/grant_retro_access', methods=['GET', 'POST'])
def grant_retro_access():
    if 'email' not in session:
        return redirect('/login')

    event = 'on grant retro access'
    user_event(event)

    datastore_client = datastore.Client()
    query = datastore_client.query(kind='RetroBoard')
    boards = query.fetch()
    email = session.get('email')
    if request.method == 'POST':
        # Get data from form
        retro_board_id = request.form.get('retro_board_id')

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
        poker_board_key = datastore_client.key('RetroBoard', retro_board_id)
        retro_board = datastore_client.get(poker_board_key)
        retro_board_name = retro_board.get('retro_board_name')

        # Check if RetroBoard entity exists
        if not retro_board:
            return jsonify({'error': 'Retro Board does not exist'}), 404

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

            # Check if the user already has access to the retro board
            retro_board_entitlements = user.get('retro_board_entitlement', [])
            retro_board_exists = any(
                entitlement.get('retro_board_id') == retro_board_id for entitlement in retro_board_entitlements
            )
            if retro_board_exists:
                flash(f'User {user["name"]} already has access to Retro Board {retro_board_name}', 'danger')
                continue  # Skip granting access to this user

            # Grant access to user by adding retro_board_id to User's list of entitlement
            retro_board_entitlements.append({'retro_board_id': retro_board_id, 'retro_board_name': retro_board_name})
            user['retro_board_entitlement'] = retro_board_entitlements
            datastore_client.put(user)

            flash(f'Access granted to user {user["name"]} for Retro Board {retro_board_name}', 'success')

        event = 'user access granted'
        user_event(event)

        return redirect('/grant_retro_access')

    

    
    # Render the HTML page for GET requests
    users_query = datastore_client.query(kind='User')
    users_query.add_filter('email', '!=', email)
    users = list(users_query.fetch())
    return render_template('grant_retro_access.html', users=users, boards=boards)


@views.route('/choose_retro_board_member', methods=['GET', 'POST'])
def choose_retro_board_member():
    if 'email' not in session:
        return redirect('/login')
    else:

        event = 'on choose retro board '
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
            retro_boards = user.get('retro_board_entitlement',[])

        if not retro_boards:
            return render_template('no_retro.html')    

        
        
        if request.method == "POST":

            retro_board_id = request.form['retro_board_id']
           
            session['retro_board_id'] = retro_board_id
           
            return redirect(url_for('views.scrum_team_retro_view',name=name))

        else:
            return render_template('choose_retro_board_member.html', name=name, retro_boards = retro_boards)


@views.route('/choose_retro_board_master', methods=['GET', 'POST'])
def choose_retro_board_master():
    if 'email' not in session:
        return redirect('/login')

    datastore_client = datastore.Client()

    retro_boards_query = datastore_client.query(kind='RetroBoard')
    retro_boards = list(retro_boards_query.fetch())

    if request.method == 'POST':
        retro_board_id = request.form.get('retro_board_id')
        session['retro_board_id'] = retro_board_id
        return redirect('/retro_results_master')
    
    else:
        return render_template('choose_retro_board_master.html', retro_boards=retro_boards)

    

    

    
