import base64
import json
import datetime
from google.cloud import datastore
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_plaintext(request):
    request_json = request.get_json(silent=True)
    if not request_json or 'plaintext' not in request_json:
        return ' Status:Failure \n Error: 400 Bad Request \n Required fields : {"plaintext","poker_board_id","team_id", "created_user_id"}'

    original_message = request_json['plaintext'].encode('utf-8')

    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(original_message)
    
    poker_board_id = request_json.get('poker_board_id')
    team_id = request_json.get('team_id')
    created_user_id = request_json.get('created_user_id')

    response_dict = {
        'poker_board_id': poker_board_id,
        'created_timestamp': datetime.datetime.utcnow().isoformat(),
        'last_modified_timestamp': datetime.datetime.utcnow().isoformat(),
        'team_id': team_id,
        'created_user_id': created_user_id,
        'encrypted_text': base64.b64encode(ciphertext).decode('utf-8'),
        
    }

    # Save response_dict to Datastore
    client = datastore.Client()
    entity_key = client.key('PokerBoard', poker_board_id)
    entity = datastore.Entity(key=entity_key)
    entity.update(response_dict)
    client.put(entity)

    #return json.dumps(response_dict)
    return "Status : Success \nSuccess Code : 201 'Created'"