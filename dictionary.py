import base64
from random import expovariate, randint
from PIL import Image, ImageFont, ImageDraw, ImageChops  # 导入模块
import io
from datetime import datetime
import json
import re
import random
from pathlib import Path
import requests

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

good_text = json.loads(Path('good_text.json').read_text(encoding='utf8'))

time_to_do = {
    0: '睡觉',
    4.5: '起床',
    7: '吃早饭',
    7.5: '学习',
    11.2: '吃午饭',
    12.5: '午休',
    13.5: '学习',
    17: '吃晚饭',
    18: '学习',
    21: '运动',
    22: '休息',
    23: '睡觉',
    25: '睡觉',
}
time_to_do_key = list(time_to_do.keys())


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


def get_date_img():
    def trim(im):
        bg = Image.new(im.mode, im.size, (255, 255, 255))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)

    im = Image.new('RGB', (800, 50), (255, 255, 255))

    draw = ImageDraw.Draw(im)  # 修改图片
    font = ImageFont.truetype('msyh.ttc', size=30)

    now = datetime.now()

    hour = now.minute/60+now.hour

    todo = '睡觉'
    for i in range(len(time_to_do)-1):
        if time_to_do_key[i] < hour < time_to_do_key[i+1]:
            todo = time_to_do[time_to_do_key[i]]
            break

    now_str = now.strftime('%H{h}%M{f}%S{s}，该{todo}了').format(
        h='时', f='分', s='秒', todo=todo)  # %Y{y}%m{m}%d{d}  # y='年', m='月', d='日',
    draw.text((0, 10), now_str, fill=(randint(100, 180), randint(
        100, 180), randint(100, 180)), font=font)  # 利用ImageDraw的内置函数，在图片上写入文字
    im = trim(im)
    width = im.size[0]
    height = im.size[1]

    new_size = (width // 20 + 1) * 25

    result = Image.new('RGB', (new_size, new_size // 2), (255, 255, 255))
    result.paste(im, (((new_size - width) // 2),
                      ((new_size // 2 - height) // 2)))

    im = result

    # im.show()

    with io.BytesIO() as output:
        im.save(output, format="PNG")
        contents = output.getvalue()

    imgurl = 'base64://' + base64.b64encode(contents).decode('ascii')
    return f'[CQ:image,file={imgurl}]'  # type=flash,


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
