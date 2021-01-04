from __future__ import unicode_literals
from plurk_oauth import PlurkAPI
from bs4 import BeautifulSoup
import requests
import datetime
import json
import time

class PlurkUser(object):
    def __init__(self):
        temp = plurk.callAPI('/APP/Users/me')
        self.user_id = temp["id"]

    def add_plurk(self, content, qualifier = '', limited_to = ''):
        temp = plurk.callAPI('/APP/Timeline/plurkAdd', options={'content': content, 'qualifier': qualifier, 'limited_to': limited_to })
        return temp

    def del_plurk(self, plurk_id):
        temp = plurk.callAPI('/APP/Timeline/plurkDelete', options={'plurk_id': plurk_id})
        return temp

    def add_response(self, plurk_id, content, qualifier = ''):
        temp = plurk.callAPI('/APP/Responses/responseAdd', options={'plurk_id': plurk_id, 'content': content, 'qualifier': qualifier})
        return temp

def message_format(plurk_id, ch, en, rel_time, intro, links):
    for t in range(0,len(ch),1):
        time.sleep(5)
        content = '電影名稱：**' + ch[t] + '** (' + en[t] + ')\n' + rel_time[t] + '\n電影簡介：' + intro[t][:200] + '\n' + links[t]
        print(content)
        #print(plurk_id)
        #
        temp = plurk.callAPI('/APP/Responses/responseAdd', options={'plurk_id': plurk_id, 'content': content, 'qualifier':''})
        #print(temp)
        #print(content)

def yahoo_movie_parser(url, plurk_id):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    movie_name = soup.find_all("div", class_="release_movie_name")
    ch_name = [i.find('a', class_='gabtn').text.replace('\n','').replace(' ','') for i in movie_name]
    en_name = [i.find('div', class_='en').find('a').text.replace('\n','').replace(' ','', 20) for i in movie_name]
    #print(ch_name)
    #print(en_name)

    movie_link = [i.find('a', class_='gabtn')['href'] for i in movie_name]
    #print(movie_link)

    release_time = [i.text for i in soup.find_all('div', class_='release_movie_time')]
    release_time = [i.replace(" ： ", "：") for i in release_time]
    #print(release_time)

    movie_info = [i.text.strip() for i in soup.find_all('div',class_="release_text")]
    intro = []
    for i in movie_info:
        temp = i.split('\r\n')
        intros = ''
        for j in temp:
            if j == '' or j.find('★') == 0 or j.find('【關於電影】') != -1 or j == '\xa0':
                continue
            intros += j
                
        intro.append(intros.strip())
    #print(intro)

    message_format(plurk_id, ch_name, en_name, release_time, intro, movie_link)

def get_next_page(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text,'html.parser')
    pageInfo = soup.find('div', class_ = 'page_numbox')
    if pageInfo == None:
        return None
    tagA = pageInfo.find('li', class_ = 'nexttxt').find('a')
    if tagA:
        return tagA['href']
    else:
        return None

def post_movie():
    temp = author.add_plurk('#movie #電影 #本週上映電影\n如果有出錯或是任何問題歡迎填[表單](https://forms.gle/EpDjFGGXouFVTiNk6)回報給作者！！','says')
    plurk_id = temp['plurk_id']
    #print(plurk_id)
    #temp = author.add_plurk('#test test message', 'says', '[15240921]')
    #print(temp['plurk_id'])
    #plurk_id = temp['plurk_id']
    #plurk_id = 0

    url = 'https://movies.yahoo.com.tw/movie_thisweek.html'
    url_list = []
    while url:
        url_list.append(url)
        url = get_next_page(url)

    for u in url_list:
        print(u)
        yahoo_movie_parser(u, plurk_id)


def main():
    global plurk, author

    plurk = PlurkAPI.fromfile('key/API.keys')
    author = PlurkUser()
    #post_movie()
    
    while True:
        if (datetime.date.today().isoweekday()) == 7 and (datetime.datetime.now().hour) == 16 and (datetime.datetime.now().minute) == 10:
            time.sleep(30)
            post_movie()
        else:
            time.sleep(0.5)
        if (datetime.datetime.now().second) == 0:
            try:
                plurk.callAPI('/APP/Alerts/addAllAsFriends')
            except:
                print('error when add friends')

if __name__ == '__main__':
    main()

