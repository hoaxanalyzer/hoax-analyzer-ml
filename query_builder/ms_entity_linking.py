########### Python 3.2 #############
from query_builder.config import microsoft_entity_linking_key as account_key
import http.client, urllib.request, urllib.parse, urllib.error, base64
import json

headers = {'Content-Type':'text/plain', 'Ocp-Apim-Subscription-Key':account_key, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36'}

def get_entity_list(text):
    params = urllib.parse.urlencode({
        # Request parameters
        'selection': '',
        'offset': '',
    })

    try:
        base_url = 'westus.api.cognitive.microsoft.com'


        conn = http.client.HTTPSConnection(base_url)
        conn.request("POST", "/entitylinking/v1.0/link?%s", text, headers)
        response = conn.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        entity_data = data["entities"]
        entities = []
        for ent in entity_data:
            entities.append(ent["matches"][0]["text"])
        print(entities)
        conn.close()
        return entities
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        return []

####################################