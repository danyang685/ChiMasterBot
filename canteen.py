import requests
import json
from bs4 import BeautifulSoup
from itertools import combinations
import random


def get_canteen_msg():
    detail = requests.get('https://canteen.sjtu.edu.cn/CARD/Ajax/Place').json()

    detail.sort(key=lambda x: x['Id'])

    result = [
        {
            'percentage': 100*canteen['Seat_u']//canteen['Seat_s'],
            'count':canteen['Seat_u'],
            'name':canteen['Name']
        }
        for canteen in detail
    ]

    msg = ''
    has = False
    for i in result:
        if i['count'] < 5:
            continue
        has = True
        msg += f"{i['name']}：目前约有{i['count']}人就餐，剩余承载力{100-i['percentage']}％\n"
    if has:
        msg = '目前开放的食堂，就餐人数情况如下：\n'+msg
    else:
        msg += "食堂都关门了，你没饭吃了！"
    msg += '原始数据来自【https://canteen.sjtu.edu.cn/】，该数据通过刷卡记录进行估算，可能与实际情况略有出入。'
    msg += '祝你用餐愉快！'
    return msg


def get_library_msg():
    detail = json.loads(requests.get(
        'http://zgrstj.lib.sjtu.edu.cn/cp').text[12:-2])['numbers']

    result = [
        {
            'percentage': 100*library['inCounter']//library['max'] if library['max'] != 0 else 0,
            'count':library['inCounter'],
            'name':library['areaName']
        }
        for library in detail
    ]

    msg = ''
    has = False
    for i in result:
        if i['count'] == 0:
            continue
        has = True
        msg += f"{i['name']}：目前约有{i['count']}人在馆，剩余承载力{100-i['percentage']}％\n"

    if has:
        msg = '目前开放的图书馆，在馆人数情况如下：\n'+msg
    else:
        msg += f"图书馆全都关门了，你没地方去了！"

    msg += '原始数据来自【http://www.lib.sjtu.edu.cn】，该数据通过入馆闸机和出馆检测仪记录和相关设定进行估算，可能与实际情况略有出入。'
    msg += '祝你在馆愉快！'
    return msg


def get_news_msg():
    return '新闻功能已关闭，请上网自行阅览！'
    s = requests.session()
    s.headers.update(
        {
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
        }
    )
    r = s.get('http://www.people.com.cn/')
    soup = BeautifulSoup(r.content, 'html5lib')
    headline = soup.find('section', {'class': 'w1000 cont_a'})
    news_links = [i['href'].strip() for i in headline.find_all('a')]
    news_links = [
        i for i in news_links if 'pic.people' not in i and 'v.people' not in i and len(i) > 58]

    news_links = list(random.choice(list(combinations(news_links, 5))))

    news_titles = []
    for news_link in news_links:
        r = s.get(news_link)
        soup = BeautifulSoup(r.content, 'html5lib')
        title = soup.find('title').text.split(
            '--')[0].replace(u'\xa0', ' ').strip()
        news_titles.append(title)

    news_titles = list(set(news_titles))

    msg = '最新要闻：\n'
    msg += '\n'.join(news_titles)
    msg += '\n——上述数据来源于《人民网》'
    return msg



