import json
import re
import random
from pathlib import Path

ci_yu = {
    item['ci']: item['explanation']
    for item in json.loads(
        Path('ci_yu.json'
             ).read_text(encoding='utf8')
    )
}
ci_yu_key = list(ci_yu.keys())
cheng_yu = {
    item['word']: item['explanation']
    for item in json.loads(
        Path('cheng_yu.json'
             ).read_text(encoding='utf8')
    )
}
cheng_yu_key = list(cheng_yu.keys())

tang_shi = json.loads(Path('tang_shi.json').read_text(encoding='utf8'))
song_ci = json.loads(Path('song_ci.json').read_text(encoding='utf8'))


def get_ci_yu():
    word = random.choice(ci_yu_key)
    explain = re.sub(r'\A[0-9]*\.', '', ci_yu[word])
    return f'【{word}】：{explain}'


def get_cheng_yu():
    word = random.choice(cheng_yu_key)
    explain = cheng_yu[word]
    return f'\n【{word}】：{explain}'


def get_tang_shi():
    shi = random.choice(tang_shi)
    return f'{shi[2]}\n《{shi[0]}》——{shi[1]}'


def get_song_ci():
    ci = random.choice(song_ci)
    return f'{ci[2]}\n《{ci[0]}》——{ci[1]}'
