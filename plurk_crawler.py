from __future__ import unicode_literals
from plurk_oauth import PlurkAPI
import pymongo
import requests
import hashlib
import logging
import json
import ast
import sys

def get_db_ids(db, collection):
    doc = conn[db][collection].find({},{"_id": 1})
    db_ids = [x["_id"] for x in doc]
    return db_ids

def convert_link_to_id(link):
    order = '0123456789abcdefghijklmnopqrstuvwxyz'
    pid = 0
    if link.find('/p/') != -1:
        sub_link = link.split('/p/')[1]

        for i in sub_link:
            pos = order.find(i)
            pid = pid * 36 + pos

    return pid

def convert_id_to_link(_id):
    try:
        _id = int(_id)
    except:
        return "Error!"
    
    order = '0123456789abcdefghijklmnopqrstuvwxyz'
    link = []
    while _id:
        _, mod = divmod(_id, 36)
        link.append(order[int(mod)])
        _id = (_id-mod) / 36
    link.reverse()

    return 'https://www.plurk.com/p/' + ''.join(link)

def crawler_responses(plurk_id, from_response_id = 0):
    print("Starting crawling the responses of ID: {}".format(plurk_id))
    url = 'https://www.plurk.com/Responses/get'
    post_data = {"plurk_id": plurk_id, "from_response_id": from_response_id}
    r = requests.post(url, data = post_data)
    if r.status_code == 400:
        #logging.info('ID: {} get some error! Error message is {}'.format(plurk_id, r.text))
        return "404"
    
    data = json.loads(r.text)
    if 'responses' in data.keys():
        for i in data['responses']:
            db_ids = get_db_ids('plurk', 'responses')
            i["_id"] = i["id"]
            sha1 = hashlib.sha1(str(i).encode('utf-8')).hexdigest()
            if i['id'] in db_ids:
                doc = conn.plurk.responses.find({"_id": i["id"]}, {"_id":0, "id": 1, "sha1": 1})
                for x in doc:
                    if sha1 == x['sha1']:
                        break
                    else:
                        conn.plurk.responses.delete_one({"_id": i["id"]})
                        i['sha1'] = sha1
                        conn.plurk.responses.insert_one(i)
            else:
                i['sha1'] = sha1
                conn.plurk.responses.insert_one(i)
    
    print('ID: {} finished!'.format(plurk_id))

def get_anonymous_plurks(offset = 0, limit = 100):
    db_ids = get_db_ids('plurk', 'anonymous')

    r = requests.get('https://www.plurk.com/Stats/getAnonymousPlurks?lang=zh&offset={}&limit={}'.format(offset, limit))
    data = json.loads(r.text)
    pids = data["pids"]
    for plurk_id in pids:
        str_id = str(plurk_id)
        data[str_id]["_id"] = plurk_id
        sha1 = hashlib.sha1(str(data[str_id]).encode('utf-8')).hexdigest()
        data[str_id]["sha1"] = sha1

        if plurk_id in db_ids:
            cache = conn.plurk.anonymous.find(
                {"_id": plurk_id},
                {"_id": 0, "sha1": 1, "id": 1}
            )

            for x in cache:
                if sha1 == x['sha1']:
                    break
                else:
                    doc = conn.plurk.anonymous.delete_one({"_id": plurk_id})
                    doc = conn.plurk.anonymous.insert_one(data[str_id])
                    logging.info('ID: {} modified!'.format(doc.inserted_id))
        else:
            doc = conn.plurk.anonymous.insert_one(data[str_id])
            logging.info(doc.inserted_id)
    
    return pids

def crawler_plurk(plurk_id):
    print("Starting crawling ID: {}".format(plurk_id))
    data = api.callAPI('/APP/Timeline/getPlurk', options={'plurk_id': plurk_id})

    if not data:
        print("ID: {} no data".format(plurk_id))
        return

    if 'error_text' in data.keys():
        print("ID: {} got some error, error_text is {}".format(plurk_id, data['error_text']))
        return
    
    if 'plurk_users' in data.keys():
        user_ids = get_db_ids('plurk', 'users')
        users = data['plurk_users']

        for i in users:
            if users[i]['id'] in user_ids:
                users[i]["_id"] = users[i]['id']
                sha1 = hashlib.sha1(str(users[i]).encode('utf-8')).hexdigest()

                doc = conn.plurk.users.find({"_id": users[i]['_id']}, {"_id": 0, "id": 1, "sha1": 1})
                for x in doc:
                    if sha1 == x['sha1']:
                        break
                    else:
                        conn.plurk.users.delete_one({"_id": users[i]['id']})
                        users[i]["sha1"] = sha1
                        conn.plurk.users.insert_one(users[i])
                    
            else:
                users[i]["_id"] = users[i]['id']
                sha1 = hashlib.sha1(str(users[i]).encode('utf-8')).hexdigest()
                users[i]["sha1"] = sha1
                conn.plurk.users.insert_one(users[i])

    if 'plurk' in data.keys():
        plurk_ids = get_db_ids('plurk', 'all_plurks')
        plurk_main = data['plurk']

        if plurk_main['plurk_id'] in plurk_ids:
            plurk_main["_id"] = plurk_main['plurk_id']
            sha1 = hashlib.sha1(str(plurk_main).encode('utf-8')).hexdigest()

            doc = conn.plurk.all_plurks.find({"_id": plurk_main['_id']}, {"_id": 0, "id": 1, "sha1": 1})
            for x in doc:
                if sha1 == x['sha1']:
                    break
                else:
                    conn.plurk.all_plurks.delete_one({"_id": plurk_main['plurk_id']})
                    plurk_main["sha1"] = sha1
                    conn.plurk.all_plurks.insert_one(plurk_main)
        else:
            plurk_main["_id"] = plurk_main['plurk_id']
            sha1 = hashlib.sha1(str(plurk_main).encode('utf-8')).hexdigest()
            plurk_main["sha1"] = sha1
            conn.plurk.all_plurks.insert_one(plurk_main)
    
    print('ID: {} finished!'.format(plurk_id))

def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == 'responses':
            for i in range(1000000000, 1452000000):
                crawler_responses(i)
        elif sys.argv[1] == 'plurk':
            for i in range(1000000000, 1452000000):
                crawler_plurk(i)
    elif len(sys.argv) == 1:
        id_list = get_anonymous_plurks()
        for _ in range(10000):
            if id_list:
                min_number = min(id_list)
                id_list = get_anonymous_plurks(min_number)
            else:
                logging.info('No other plurks!')
                break

if __name__ == '__main__':
    api = PlurkAPI.fromfile('key/API.keys')
    conn = pymongo.MongoClient(host='127.0.0.1', port=27017)
    log_format = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format, filename='anonymous_crawler.log')
    main()
