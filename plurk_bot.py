from __future__ import unicode_literals
from plurk_oauth import PlurkAPI
from bs4 import BeautifulSoup
import requests
import datetime
import time

class PlurkUser():
    def __init__(self):
        self._id = plurk.callAPI('/APP/Users/me')['id']
    
    def add_plurk(self, content, qualifier = '', limited_to = ''):
        ret = plurk.callAPI(
            '/APP/Timeline/plurkAdd', 
            options={
                'content': content, 
                'qualifier': qualifier, 
                'limited_to': limited_to 
            }
        )

        return ret

    def add_response(self, plurk_id, content, qualifier = ''):
        ret = plurk.callAPI(
            '/APP/Responses/responseAdd', 
            options={
                'plurk_id': plurk_id, 
                'content': content, 
                'qualifier': qualifier
            }
        )

        return ret
    
    def get_id(self):
        return self._id

def plurk_message_format(plurk_id, ch_name, en_name, movie_link, release_time, introduction):
    content = '電影名稱：**' + ch_name + '** (' + en_name + ')\n' + release_time + '\n電影簡介：' + introduction[:200] + '\n' + movie_link
    print(content)
    resp_ret = plurk.callAPI(
        '/APP/Responses/responseAdd', 
        options={
            'plurk_id': plurk_id, 
            'content': content, 
            'qualifier': ''
        }
    )

def movie_nextweek():
    temp = bot.add_plurk('#movie #電影 #本週上映電影\n如果有出錯或是任何問題歡迎填[表單](https://forms.gle/EpDjFGGXouFVTiNk6)回報給作者！！','says')
    plurk_id = temp['plurk_id']

    url = "https://movies.yahoo.com.tw/movie_thisweek.html"
    while url:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

        release_info = soup.find_all("div", class_="release_info")
        for i in release_info:
            movie_name = i.find("div", class_="release_movie_name")
            ch_name = movie_name.find('a', class_='gabtn').text.replace('\n','').replace(' ','')
            en_name = movie_name.find('div', class_='en').find('a').text.replace('\n','').replace(' ','', 20)
            movie_link = movie_name.find('a', class_='gabtn')['href']
            release_time = i.find('div', class_='release_movie_time').text.replace(" ： ", "：")
            movie_info = i.find('div',class_="release_text").text.strip()
            temp = movie_info.split('\r\n')
            introduction = ''
            for j in temp:
                if j == '' or j.find('★') == 0 or j.find('【關於電影】') != -1 or j == '\xa0':
                    continue
                introduction += j
            introduction = introduction.strip()

            plurk_message_format(plurk_id, ch_name, en_name, movie_link, release_time, introduction)
        
        page_info = soup.find('div', class_ = 'page_numbox')
        if page_info == None:
            break
        else:
            page_link = page_info.find('li', class_='nexttxt').find('a')
            if page_link:
                url = page_link['href']
            else:
                break

def main():
    while True:
        if (datetime.date.today().isoweekday()) == 7 and (datetime.datetime.now().hour) == 16 and (datetime.datetime.now().minute) == 10:
            time.sleep(30)
            movie_nextweek()
        else:
            time.sleep(0.5)
        if (datetime.datetime.now().second) == 0:
            active_notify = plurk.callAPI('/APP/Alerts/getActive')
            for i in active_notify:
                if i['type'] == 'friendship_request':
                    friends_ret = plurk.callAPI(
                        '/APP/Alerts/addAsFriend',
                        options={
                            "user_id": i['from_user']['id']
                        } 
                    )

if __name__ == '__main__':
    plurk = PlurkAPI.fromfile('key/API.keys')
    bot = PlurkUser()
    main()
