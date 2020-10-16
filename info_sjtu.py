import requests
import json
from ids import get_buildings_headcount


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


def get_classroom_msg():
    result = get_buildings_headcount()
    msg = ''
    has = False

    for i in result:
        if i['count'] == 0:
            continue
        has = True
        msg += f"{i['name']}：目前约有{i['count']}人在教室，剩余承载力{100-i['percentage']}％\n"

    if has:
        msg = '目前开放的教学楼，室内人数情况如下：\n'+msg
    else:
        msg += f"教学楼全都关门了，你没地方去了！"

    msg += '原始数据来自【http://ids.sjtu.edu.cn】，该数据通过室内摄像头定时截图并使用人工智能算法进行计数，可能与实际情况略有出入。'
    msg += '祝你在教室愉快！'
    return msg
