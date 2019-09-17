from __future__ import unicode_literals
from plurk_oauth import PlurkAPI
import requests
import json
import ast

class PlurkMain(object):
    def __init__(self, plurk_id):
        self.plurk_id = plurk_id
    
    def get_information(self, plurk_id):
        content = plurk.callAPI('/APP/Timeline/getPlurk', options={'plurk_id': plurk_id})
        #print(json.dumps(content, ensure_ascii=False, indent=4))        
        print(content["plurk"]["user_id"])
        print(content["plurk"]["content"])
        print(content["plurk"]["posted"])
        print(content["plurk"]["response_count"])

class PlurkResponse(object):
    def __init__(self, plurk_id):
        self.plurk_id = plurk_id

class PlurkUser(object):
    def __init__(self):
        temp = plurk.callAPI('/APP/Users/me')
        self.user_id = temp["id"]

    def add_plurk(self, content, qualifier = 'says'):
        temp = plurk.callAPI('/APP/Timeline/plurkAdd', options={'content': content, 'qualifier': qualifier})
        return temp

    def del_plurk(self, plurk_id):
        temp = plurk.callAPI('/APP/Timeline/plurkDelete', options={'plurk_id': plurk_id})
        return temp

def get_anonymous_plurks(offset = 0, limit = 10):
    r = requests.get('https://www.plurk.com/Stats/getAnonymousPlurks?lang=zh&offset=' + offset.__str__() + '&limit=' + limit.__str__())
    plurk_id = json.dumps(json.loads(r.text)["pids"], ensure_ascii=False, indent=4)
    return plurk_id

def main():
    global plurk
    id_list = get_anonymous_plurks(0, 1)
    ids = ast.literal_eval(id_list)
    print(ids[0])

    plurk = PlurkAPI.fromfile('key/API.keys')
    author = PlurkUser()
    author.add_plurk('Post By API')
    plurks = PlurkMain(ids[0])
    plurks.get_information(ids[0])

if __name__ == '__main__':
    main()
