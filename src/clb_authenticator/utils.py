from base64 import b64decode
import json

def padded(s):
    return s + '='*(4-len(s) % 4)

def get_payload(jwt_token):
    """Obtain the payload from a jwt token without validating it.

    Args:
       jwt_token (bytes): jwt_token

    Return:
       payload (dict): token payload
    """
    encoded_payload = jwt_token.split(b'.')[1]
    json_payload = b64decode(padded(encoded_payload))
    return json.loads(json_payload)
