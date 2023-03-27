import base64
import json
import datetime
from google.cloud import datastore

def update_poker_board(request):
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
    updated_user = False
    
    for estimate in estimates:
        if estimate.get('jira_id') == jira_id:
            users = estimate.get('users', [])
            for user in users:
                if user.get('user_id') == user_id:
                    user['story_point'] = story_point
                    user['created_timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                    updated_user = True
                    updated_estimate = True
                    break
            if not updated_user:
                users.append({'user_id': user_id, 'story_point': story_point, 'created_timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')})
                estimate['users'] = users
                updated_estimate = True
    
    if not updated_estimate:
        estimates.append({'jira_id': jira_id, 'users': [{'user_id': user_id, 'story_point': story_point, 'created_timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')}]})
    
    entity.update({'estimates': estimates, 'last_modified_timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')})
    client.put(entity)
    
    return json.dumps(entity, default=str)
