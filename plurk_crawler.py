from plurk_oauth import PlurkAPI
import pymongo
import hashlib
import logging
import sys

class Plurk(object):
    def __init__(self, plurk_id):
        self.plurk_id = plurk_id
        data = api.callAPI('/APP/Timeline/getPlurk', options={'plurk_id': self.plurk_id})
        
        if data == None:
            logging.info(f"Get nothing of ID: {self.plurk_id}")
            self.users = None
            self.headers = None
        else:
            logging.info(f"Request header and user of ID: {self.plurk_id}")
            self.headers = data['plurk']
            self.users = data['plurk_users']
    
    def insert_header(self):
        doc_num = conn.plurk.all_plurks.count_documents({"_id": self.headers["plurk_id"]})
        if doc_num:
            self.headers["_id"] = self.headers["plurk_id"]
            sha1 = hashlib.sha1(str(self.headers).encode('utf-8')).hexdigest()

            resp_doc = conn.plurk.all_plurks.find({"_id": self.headers["_id"]}, {"_id": 0, "id": 1, "sha1": 1})
            for x in resp_doc:
                if sha1 == x['sha1']:
                    break
                else:
                    conn.plurk.all_plurks.delete_one({"_id": self.headers["_id"]})
                    self.headers["sha1"] = sha1
                    conn.plurk.all_plurks.insert_one(self.headers)
        else:
            self.headers["_id"] = self.headers['plurk_id']
            sha1 = hashlib.sha1(str(self.headers).encode('utf-8')).hexdigest()
            self.headers["sha1"] = sha1
            conn.plurk.all_plurks.insert_one(self.headers)

    def insert_users(self):
        for user_id in self.users:
            self.users[user_id]["_id"] = user_id
            sha1 = hashlib.sha1(str(self.users[user_id]).encode('utf-8')).hexdigest()

            doc_num = conn.plurk.users.count_documents({"_id": self.users[user_id]["_id"]})
            if doc_num:
                resp_doc = conn.plurk.users.find({"_id": self.users[user_id]["_id"]}, {"_id":0, "id": 1, "sha1": 1})
                for x in resp_doc:
                    if sha1 == x["sha1"]:
                        break
                    else:
                        conn.plurk.users.delete_one({"_id": self.users[user_id]["_id"]})
                        self.users[user_id]["sha1"] = sha1
                        conn.plurk.users.insert_one(self.users[user_id])
            else:
                self.users[user_id]["sha1"] = sha1
                conn.plurk.users.insert_one(self.users[user_id])

    def convert_id_to_link(self):
        order = '0123456789abcdefghijklmnopqrstuvwxyz'
        link = []
        while self.plurk_id:
            _, mod = divmod(self.plurk_id, 36)
            link.append(order[int(mod)])
            self.plurk_id = (self.plurk_id-mod) / 36
        link.reverse()

        return 'https://www.plurk.com/p/' + ''.join(link)

class PlurkResponses(object):
    def __init__(self, plurk_id):
        self.plurk_id = plurk_id
        logging.info(f"Request response data of ID: {self.plurk_id}")
        resp = api.callAPI('/APP/Responses/getById', options={'plurk_id': self.plurk_id})
        self.users = resp['friends']
        self.responses = resp['responses']

    def insert_responses(self):
        for resp in self.responses:
            resp["_id"] = resp["id"]
            sha1 = hashlib.sha1(str(resp).encode('utf-8')).hexdigest()

            doc_num = conn.plurk.responses.count_documents({"_id": resp["id"]})
            if doc_num:
                resp_doc = conn.plurk.responses.find({"_id": resp["_id"]}, {"_id": 0, "sha1": 1})
                for x in resp_doc:
                    if sha1 == x["sha1"]:
                        break
                    else:
                        conn.plurk.responses.delete_one({"_id": resp["id"]})
                        resp["sha1"] = sha1
                        conn.plurk.responses.insert_one(resp)
            else:
                resp["sha1"] = sha1
                conn.plurk.responses.insert_one(resp)
    
    def insert_users(self):
        for user_id in self.users:
            self.users[user_id]["_id"] = user_id
            sha1 = hashlib.sha1(str(self.users[user_id]).encode('utf-8')).hexdigest()

            doc_num = conn.plurk.users.count_documents({"_id": self.users[user_id]["_id"]})
            if doc_num:
                resp_doc = conn.plurk.users.find({"_id": self.users[user_id]["_id"]}, {"_id":0, "id": 1, "sha1": 1})
                for x in resp_doc:
                    if sha1 == x["sha1"]:
                        break
                    else:
                        conn.plurk.users.delete_one({"_id": self.users[user_id]["_id"]})
                        self.users[user_id]["sha1"] = sha1
                        conn.plurk.users.insert_one(self.users[user_id])
            else:
                self.users[user_id]["sha1"] = sha1
                conn.plurk.users.insert_one(self.users[user_id])

def main():
    if len(sys.argv) == 3:
        for i in range(int(sys.argv[1]), int(sys.argv[2])):
            crawler_plurk = Plurk(i)
            if crawler_plurk.headers:
                crawler_plurk.insert_header()
                crawler_plurk.insert_users()
                crawler_response = PlurkResponses(i)
                crawler_response.insert_responses()
                crawler_response.insert_users()

if __name__ == "__main__":
    api = PlurkAPI.fromfile('key/API.keys')
    conn = pymongo.MongoClient(host='127.0.0.1', port=27017)
    log_format = '%(asctime)s %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)
    main()
