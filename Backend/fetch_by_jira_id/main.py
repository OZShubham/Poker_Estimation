from google.cloud import datastore
import json    

def get_data_by_jira_id(request):
    request_json = request.get_json(silent=True)
    if not request_json or 'jira_id' not in request_json or 'poker_board_id' not in request_json:
        return 'Error: jira_id or poker_board_id field not provided in request.'
    poker_board_id = request_json.get('poker_board_id')
    jira_id = request_json.get('jira_id')
    
    client = datastore.Client()
    entity_key = client.key('PokerBoard', poker_board_id)
    entity = client.get(entity_key)
    if not entity:
        return 'Error: No entity found with given jira_id'    

    estimates = entity.get('estimates', [])
    for estimate in estimates:
        if estimate.get('jira_id') == jira_id:
            return json.dumps(estimate)