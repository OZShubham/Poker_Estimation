from google.cloud import datastore
import json

def get_data(request):
  request_json = request.get_json(silent=True)
  if not request_json or 'poker_board_id' not in request_json:
    return ' Status:Failure \n Error: 400 Bad Request \n Required fields : {"poker_board_id"}'
  poker_board_id = request_json.get('poker_board_id')  

  client = datastore.Client()
  entity_key = client.key('PokerBoard', poker_board_id)
  entity = client.get(entity_key)
  
  

  return json.dumps(entity)
