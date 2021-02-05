import base64
from random import expovariate, randint
from PIL import Image, ImageFont, ImageDraw, ImageChops  # 导入模块
import colorsys
import io
from datetime import datetime
import json
import re
import random
from pathlib import Path


class Jsonobj:
    def __init__(self, obj, key):
        self.obj = obj
        self.key = key


class Lazyload_jsonobj:
    def __init__(self, filename, loader=lambda x: x, chooser=lambda x: random.choice(x.obj), key_gen=None):
        self.filename = filename
        self.loader = loader
        self.chooser = chooser
        self.key_gen = key_gen

        self.loaded = False

    def load_obj(self):
        obj = self.loader(json.loads(
            Path(self.filename).read_text(encoding='utf8')))
        key = self.key_gen(obj) if self.key_gen else None
        self.obj = Jsonobj(obj, key)
        self.loaded = True

    def choose_one(self):
        if not self.loaded:
            self.load_obj()
        return self.chooser(self.obj)


def ci_yu_chooser(obj):
    # return 'None'
    word = random.choice(obj.key)
    explain = re.sub(r'\A[0-9]*\.', '', obj.obj[word])
    return f'【{word}】：{explain}'


ci_yu = Lazyload_jsonobj(
    filename='ci_yu.json',
    loader=lambda x: {item['ci']: item['explanation'] for item in x},
    key_gen=lambda x: list(x.keys()),
    chooser=ci_yu_chooser
)


def cheng_yu_chooser(obj):
    word = random.choice(obj.key)
    explain = obj.obj[word]
    return f'\n【{word}】：{explain}'


cheng_yu = Lazyload_jsonobj(
    filename='cheng_yu.json',
    loader=lambda x: {item['word']: item['explanation'] for item in x},
    key_gen=lambda x: list(x.keys()),
    chooser=cheng_yu_chooser
)

tang_shi = Lazyload_jsonobj(
    filename='tang_shi.json'
)
song_ci = Lazyload_jsonobj(
    filename='song_ci.json'
)


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
    return ci_yu.choose_one()


def get_cheng_yu():
    return cheng_yu.choose_one()


def get_tang_shi():
    shi = tang_shi.choose_one()
    return f'{shi[2]}\n《{shi[0]}》——{shi[1]}'


def get_song_ci():
    ci = song_ci.choose_one()
    return f'{ci[2]}\n《{ci[0]}》——{ci[1]}'


def create_img_base64(text, color):
    def trim(im):
        bg = Image.new(im.mode, im.size, (255, 255, 255))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)

    im = Image.new('RGB', (1000, 50), (255, 255, 255))

    draw = ImageDraw.Draw(im)  # 修改图片
    font = ImageFont.truetype('msyh.ttc', size=30)

    # 利用ImageDraw的内置函数，在图片上写入文字
    draw.text((0, 10), text, fill=color, font=font)
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

    return base64.b64encode(contents).decode('ascii')


def get_date_img():
    now = datetime.now()

    hour = now.minute/60+now.hour

    todo = '睡觉'
    for i in range(len(time_to_do)-1):
        if time_to_do_key[i] < hour < time_to_do_key[i+1]:
            todo = time_to_do[time_to_do_key[i]]
            break

    # %Y{y}%m{m}%d{d}  # h='时', f='分', s='秒', y='年', m='月', d='日'
    now_str = f"时间：{now.strftime('%H:%M:%S')}，该{todo}了"

    imgurl = 'base64://' + \
        create_img_base64(
            now_str, tuple([int(i*255)
                            for i in colorsys.hsv_to_rgb(random.random(), 0.7, 0.6)])
        )
    return f'[CQ:image,file={imgurl}]'  # type=flash,
