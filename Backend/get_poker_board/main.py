from google.cloud import datastore
import json

def get_poker_board(request):
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
    
    return json.dumps(entity, default=str)

