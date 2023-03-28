from google.cloud import datastore
import json

def get_story_points(request):
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
    
    # Extract the Jira IDs and story points from the PokerBoard entity
    estimates = entity.get('estimates', [])
    story_points = []
    for estimate in estimates:
        jira_id = estimate.get('jira_id')
        users = estimate.get('users', [])
        for user in users:
            user_id = user.get('user_id')
            story_point = user.get('story_point')
            story_points.append({'Jira-id': jira_id, 'Story point': story_point})

    return json.dumps(story_points)
