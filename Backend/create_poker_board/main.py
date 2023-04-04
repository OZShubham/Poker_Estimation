import base64
import json
import datetime
import hashlib
from google.cloud import datastore

def create_board_id(user_id):
    current_time = datetime.datetime.now().strftime("%d%m%y")
    board_id_str = "poker_board" + user_id + current_time
    hash_value = hashlib.md5(board_id_str.encode('utf-8')).hexdigest()
    return hash_value

def create_poker_board(request):
    request_json = request.get_json(silent=True)
    if not request_json or 'team_id' not in request_json or 'user_role' not in request_json or 'user_id' not in request_json or 'poker_board_type' not in request_json:
        return 'Status:Failure \n Error: 400 Bad Request \n Required fields : {"team_id",  "user_role","poker_board_type", "user_id"}'

    poker_board_id = create_board_id(request_json.get('user_id'))

    response_dict = {
        'poker_board_id': poker_board_id,
        'poker_board_type': request_json.get('poker_board_type'),
        'org_id': 'cognizant',
        'created_timestamp': datetime.datetime.utcnow(),
        'last_modified_timestamp': datetime.datetime.utcnow(),
        'team_id': request_json.get('team_id'),
        'user_role' : request_json.get('user_role'),
        'status' : 'Created',
        
    }

    # Save response_dict to Datastore
    client = datastore.Client()
    entity_key = client.key('PokerBoard', poker_board_id)
    entity = datastore.Entity(key=entity_key)
    entity.update(response_dict)
    client.put(entity)

    return json.dumps(response_dict, default=str)
