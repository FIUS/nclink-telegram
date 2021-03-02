import requests
import json
import config

def order_drink(user,drink,user_callback):
    r = requests.post(config.url + "/login", data={'password': config.password})
    json_result = json.loads(r.text)
    token=json_result[u'token']

    success=True

    if not r.ok:
        success=False

    r = requests.post(config.url + "/orders",
                        headers={'X-Auth-Token': token},
                        params={'user': user, 'beverage': drink})
    
    if not r.ok:
        success=False
    
    if not success:
        user_callback("Drink maybe not added")