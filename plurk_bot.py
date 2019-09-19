from __future__ import unicode_literals
from plurk_oauth import PlurkAPI
from bs4 import BeautifulSoup
import requests
import json

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

def message_format(plurk_id, ch, en, rel_time, intro, links):
    for t in range(0,len(ch),1):
        content = '電影名稱 ： **' + ch[t] + '** (' + en[t] + ')\n' + rel_time[t] + '\n電影簡介 ： ' + intro[t][:200] + '\n' + links[t]
        plurk.callAPI('/APP/Responses/responseAdd', options={'plurk_id': plurk_id, 'content': content, 'qualifier':''})
    #print(temp)

def yahoo_movie_parser(url, plurk_id):
    r = requests.get(url)
    soup = BeautifulSoup(r.text,'html.parser')

    movie_name = soup.find_all('div', class_= "release_movie_name")
    name_ch = []
    for t in movie_name:
        temp = t.find('a', class_='gabtn').text.replace('\n','').replace(' ','')
        name_ch.append(temp)
    name_en = []
    for t in movie_name:
        temp = t.find('div', class_='en').find('a').text.replace('\n','').replace(' ','', 20)
        name_en.append(temp)
    #print(name_ch)
    #print(name_en)

    movie_link = soup.find_all('div',class_="release_btn color_btnbox")
    links = []
    for t in movie_link:
        if t.find('a', class_ = "gabtn"):
            links.append(t.find('a',class_="gabtn")['href'])
        else:
            links.append('')
    #print(links)

    movie_time = soup.find_all('div', class_ = 'release_info_text')
    release_time = []
    for t in movie_time:
        temp = t.find('div', class_ = 'release_movie_time').text
        release_time.append(temp)
    #print(release_time)

    movie_intro = soup.find_all('div',class_="release_text")
    intro = []
    for t in movie_intro:
        temp = t.find('span').text
        while True:
            a = temp.find('★')
            if a == -1:
                break
            b = temp.find('\r\n')
            temp = temp.replace(temp[a:b+2], '', 1)
            #print(temp)
        intro.append(temp.replace('\n','').replace('\r','').replace('\xa0',''))
    #print(intro[0])

    message_format(plurk_id, name_ch, name_en, release_time, intro, links)

def get_next_page(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text,'html.parser')
    pageInfo = soup.find('div', class_ = 'page_numbox')
    tagA = pageInfo.find('li', class_ = 'nexttxt').find('a')
    if tagA:
        return tagA['href']
    else:
        return None

def main():
    global plurk, author

    plurk = PlurkAPI.fromfile('key/API.keys')
    author = PlurkUser()
    temp = author.add_plurk('本週上映電影')
    plurk_id = temp['plurk_id']

    url = 'https://movies.yahoo.com.tw/movie_thisweek.html'
    url_list = []
    while url:
        url_list.append(url)
        url = get_next_page(url)

    for u in url_list:
        yahoo_movie_parser(u, plurk_id)

if __name__ == '__main__':
    main()

