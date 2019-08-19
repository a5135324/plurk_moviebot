from __future__ import unicode_literals
from plurk_oauth import PlurkAPI
import requests
import json

class Plurk_Crawler():
    def __init__(self, pid):
        self.id = pid;
        self.plurk_id = pid;

def get_anonymous_plurks(offset, limit):
    plurks = requests.get('https://www.plurk.com/Stats/getAnonymousPlurks?lang=zh&offset='+ offset.__str__() + '&limit=' + limit.__str__())

plurk = PlurkAPI('key', 'secret')
plurk.authorize('token', 'token_secret')

r = requests.get("https://www.plurk.com/Stats/getAnonymousPlurks?lang=zh&offset=0&limit=2")
a = json.loads(r.text)
anony = json.dumps(a["pids"][0], ensure_ascii=False)

content = plurk.callAPI('/APP/Timeline/getPlurk', options={'plurk_id': anony})
print(json.dumps(content, ensure_ascii=False, indent=4))

temp = plurk.callAPI('/APP/Responses/get', options={'plurk_id': anony})
print(json.dumps(temp, ensure_ascii=False, indent=4))
