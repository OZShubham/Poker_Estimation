import base64
import json
import datetime
from google.cloud import datastore

def add_estimate(request):
    request_json = request.get_json(silent=True)
    if not request_json or 'poker_board_id' not in request_json:
        return 'Error: No poker_board_id field provided in request.'
    
    poker_board_id = request_json['poker_board_id']
    
    # Retrieve the PokerBoard entity from Datastore
    client = datastore.Client()
    entity_key = client.key('PokerBoard', poker_board_id)
    entity = client.get(entity_key)
    if not entity:
        return 'Error: No entity found with poker_board_id {}'.format(poker_board_id)
    
    # Update the entity with new estimate
    estimates = entity.get('estimates', [])
    jira_id = request_json.get('jira_id')
    user_id = request_json.get('user_id')
    story_point = request_json.get('story_point')
    updated_estimate = False
    
    for estimate in estimates:
        if estimate.get('jira_id') == jira_id:
            users = estimate.get('users', [])
            users.append({'user_id': user_id, 'story_point': story_point})
            estimate.update({'users': users})
            updated_estimate = True
            break
    
    if not updated_estimate:
        estimates.append({'jira_id': jira_id, 'users': [{'user_id': user_id, 'story_point': story_point}]})
    
    entity.update({'estimates': estimates, 'last_modified_timestamp': datetime.datetime.utcnow().isoformat()})
    client.put(entity)
    
    return json.dumps(entity)
