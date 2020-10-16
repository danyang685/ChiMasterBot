import json
import random
from pathlib import Path
from itertools import combinations
import requests
from bs4 import BeautifulSoup


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


good_text = json.loads(Path('good_text.json').read_text(encoding='utf8'))


def get_good_text():
    for i in range(5):
        try:
            r = requests.get('https://chp.shadiao.app/api.php').text.strip()
            if r not in good_text:
                good_text.append(r)
        except:
            pass
    good_text.sort()
    Path('good_text.json').write_text(json.dumps(
        good_text, ensure_ascii=False, indent=2), encoding='utf8')

    return random.choice(good_text)
