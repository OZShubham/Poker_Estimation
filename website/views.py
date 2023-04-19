from flask import Blueprint, render_template,url_for,request,session,redirect
from google.cloud import datastore
import json
import base64
import base64
import json
import datetime
import hashlib
from flask import Flask, jsonify, request
from google.cloud import datastore
from google.cloud.exceptions import GoogleCloudError, ClientError

views = Blueprint('views', __name__)




@views.route('/scrum_master_view')
def scrum_master_view():
    return render_template('scrum_master_view.html')

@views.route('/scrum_team_member_view')
def scrum_team_member_view():
    return render_template('team_view.html')

def create_board_id(user_id):
    current_time = datetime.datetime.now().strftime("%d%m%y")
    board_id_str = "poker_board" + user_id + current_time
    hash_value = hashlib.md5(board_id_str.encode('utf-8')).hexdigest()
    return hash_value

@views.route('/create_poker_board', methods=['GET','POST'])
def create_poker_board():
    try:
        # Check if user is logged in
        if 'email' not in session:
            return redirect('/login')
        

        email = session['email']
        team_id = request.form.get['team_id']
        user_role = request.form.get['user_role']
        poker_board_type = request.form.get['poker_board_type']
        if not team_id or not user_role or not poker_board_type:
            return jsonify({'error': 'Bad Request. Required fields are missing in the request body.'}), 400

        poker_board_id = create_board_id(email)
        print(poker_board_id)

        response_dict = {
            'user_id' : email,
            'poker_board_id': poker_board_id,
            'poker_board_type': poker_board_type,
            'org_id': 'cognizant',
            'created_timestamp': datetime.datetime.utcnow(),
            'last_modified_timestamp': datetime.datetime.utcnow(),
            'team_id': team_id,
            'user_role' : user_role,
            'status' : 'Created',
        }

        print(response_dict)

        # Save response_dict to Datastore
        client = datastore.Client()
        entity_key = client.key('PokerBoard', poker_board_id)
        entity = datastore.Entity(key=entity_key)
        entity.update(response_dict)
        client.put(entity)

        return jsonify(response_dict), 200

    except (GoogleCloudError, ClientError) as e:
        return jsonify({'error': 'Failed to create Poker Board. {}'.format(str(e))}), 500

    except Exception as e:
        return jsonify({'error': 'Internal Server Error: {}'.format(str(e))}), 500



@views.route('/t-shirt')
def tshirt():
    return render_template('t-shirt.html')

@views.route('/')
def home():
    return render_template('home.html')







