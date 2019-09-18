from __future__ import unicode_literals
from plurk_oauth import PlurkAPI
from bs4 import BeautifulSoup
import pandas as pd
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

    def add_plurk(self, content, qualifier = ''):
        temp = plurk.callAPI('/APP/Timeline/plurkAdd', options={'content': content, 'qualifier': qualifier})
        return temp

    def del_plurk(self, plurk_id):
        temp = plurk.callAPI('/APP/Timeline/plurkDelete', options={'plurk_id': plurk_id})
        return temp

    def add_response(self, plurk_id, content, qualifier = ''):
        temp = plurk.callAPI('/APP/Responses/responseAdd', options={'plurk_id': plurk_id, 'content': content, 'qualifier': qualifier})
        return temp

def get_anonymous_plurks(offset = 0, limit = 10):
    r = requests.get('https://www.plurk.com/Stats/getAnonymousPlurks?lang=zh&offset=' + offset.__str__() + '&limit=' + limit.__str__())
    plurk_id = json.dumps(json.loads(r.text)["pids"], ensure_ascii=False, indent=4)
    return plurk_id

def yahoo_movie_parser():
    url = 'https://movies.yahoo.com.tw/movie_thisweek.html'
    r = requests.get(url)
    web_content = r.text
    soup = BeautifulSoup(web_content,'html.parser')
    newMovie = soup.find_all('div', class_= "release_movie_name")
    #print(newMovie)
    NameCHs = [t.find('a', class_='gabtn').text.replace('\n','').replace(' ','') for t in newMovie]
    #print(NameCHs)
    NameENs = [t.find('div', class_='en').find('a').text.replace('\n','').replace(' ','', 20) for t in newMovie]
    #print(NameENs)
    newMovie3 = soup.find_all('div',class_="release_btn color_btnbox")
    #print(newMovie3)
    links = []
    for t in newMovie3:
        if t.find('a', class_ = "btn_s_vedio gabtn"):
            links.append(t.find('a',class_="btn_s_vedio gabtn")['href'])
        else:
            links.append('')
    #print(links)
    newMovie4 = soup.find_all('div', class_ = 'release_info_text')
    #print(newMovie4)
    release_time = [t.find('div', class_ = 'release_movie_time').text for t in newMovie4]
    #print(release_time)
    '''
    newMovie4 = soup.find_all('div',class_="release_text")
    #print(newMovie4)
    Intros = [t.find('span').text.replace('\n','').replace('\r','').replace('\xa0','').replace(' ','') for t in newMovie4]
    #print(Intros)
    '''
    df = pd.DataFrame(
    {
        'Name':NameCHs,
        'EnName':NameENs,
        'ReTime': release_time,
        'Trailer': links
    })
    print(df['Trailer'])
    

def main():
    global plurk
    '''
    id_list = get_anonymous_plurks(0, 1)
    ids = ast.literal_eval(id_list)
    print(ids[0])
    plurks = PlurkMain(ids[0])
    plurks.get_information(ids[0])
    '''

    plurk = PlurkAPI.fromfile('key/API.keys')
    author = PlurkUser()
    #temp = author.add_plurk('本週上映電影')
    #print(temp['plurk_id'])
    # 1420558413
    plurk.callAPI('/APP/Responses/responseAdd', options={'plurk_id': '1420558413', 'content': 'test\ntest', 'qualifier':''})

    
    #yahoo_movie_parser()

if __name__ == '__main__':
    main()
