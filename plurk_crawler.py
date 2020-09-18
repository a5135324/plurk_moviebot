from __future__ import unicode_literals
from plurk_oauth import PlurkAPI
import pymongo
import requests
import hashlib
import logging
import json
import ast

def get_db_ids():
    doc = conn.plurk.anonymous.find(
        {},
        {"_id": 0, "id": 1}
    )

    db_ids = [x['id'] for x in doc]
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

def dump_db(db, collection, filename):
    doc = conn[db][collection].find({})

    with open(filename, 'w', encoding='utf-8') as w:
        w.write('[')
        for x in doc:
            w.write(json.dumps(x, ensure_ascii=False))
            w.write(',')
        w.write(']')

def get_responses(plurk_id, from_response_id = 0):
    url = 'https://www.plurk.com/Responses/get'
    post_data = {"plurk_id": plurk_id, "from_response_id": from_response_id}
    r = requests.post(url, data = post_data)
    if r.status_code == 400:
        logging.info('ID: {} get some error!'.format(plurk_id))

def get_anonymous_plurks(offset = 0, limit = 100):
    db_ids = get_db_ids()

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

def main():
    id_list = get_anonymous_plurks()
    for _ in range(10000):
        if id_list:
            min_number = min(id_list)
            id_list = get_anonymous_plurks(min_number)
        else:
            logging.info('No other plurks!')
            break

if __name__ == '__main__':
    conn = pymongo.MongoClient(host='127.0.0.1', port=27017)
    log_format = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format, filename='anonymous_crawler.log')
    main()
