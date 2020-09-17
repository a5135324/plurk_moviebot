from __future__ import unicode_literals
from plurk_oauth import PlurkAPI
from bs4 import BeautifulSoup
import pandas as pd
import pymongo
import requests
import hashlib
import logging
import json
import ast

def get_db_ids():
    db_ids = []
    doc = conn.plurk.anonymous.find(
        {},
        {"_id": 0, "id": 1}
    )

    for x in doc:
        db_ids.append(x['id'])

    return db_ids

def get_response(plurk_id, from_response_id = 0):
    url = 'https://www.plurk.com/Responses/get'

def get_anonymous_plurks(offset = 0, limit = 100):
    db_ids = get_db_ids()

    r = requests.get('https://www.plurk.com/Stats/getAnonymousPlurks?lang=zh&offset={}&limit={}'.format(offset, limit))
    data = json.loads(r.text)
    for plurk_id in data['pids']:
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
    
    pids = json.dumps(json.loads(r.text)["pids"], ensure_ascii = False, indent=4)
    return pids

def main():
    id_list = get_anonymous_plurks()
    for _ in range(10000):
        ids = ast.literal_eval(id_list)
        if ids:
            min_number = min(ids)
            id_list = get_anonymous_plurks(min_number)
        else:
            logging.info('No other plurks!')
            break

if __name__ == '__main__':
    conn = pymongo.MongoClient(host='127.0.0.1', port=27017)
    log_format = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format, filename='anonymous_crawler.log')
    main()
