import requests
import re


def get_buildings():
    return {i['id']: i['name'] for i in requests.post(
        'http://ids.sjtu.edu.cn/build/findAreaBuild',
        data={'schoolArea': 0}
    ).json()['data']['buildList'][0]['children']}


def safeparse(text, parser):
    text = str(text)
    if text == '--':
        return 0
    else:
        other_text = re.sub(r'[0-9\.]', '', text)
        if other_text:
            if other_text == '-':
                text = text.split('-')[-1]
            else:
                print(text)
                return 0
        return parser(text)


def get_classrooms(building_id):
    r = [i for i in requests.post(
        'http://ids.sjtu.edu.cn/build/findBuildRoomType',
        data={'buildId': building_id}
    ).json()['data']['floorList']]
    rooms = []

    for i in r:
        rooms.extend(i['children'])
    retained_fields = {
        'id': 'roomCode',
        'name': 'name',
        'seats': 'zws',
        'i_temp': 'sensorTemp',
        'i_hum': 'sensorHum',
        'i_lux': 'sensorLux',
        'i_co2': 'sensorCo2',
        'i_pm25': 'sensorPm25',
        'headcount': 'actualStuNum',
        # 'courses':'roomCourseList',
        'free': 'freeRoom'
    }
    rooms_new = []
    for i in rooms:
        item = {}
        for k, v in retained_fields.items():
            if v in i:
                item[k] = i[v]
            else:
                item[k] = 0
        item['seats'] = safeparse(item['seats'], int)
        item['i_temp'] = safeparse(item['i_temp'], float)
        item['i_hum'] = safeparse(item['i_hum'], float)
        item['i_lux'] = safeparse(item['i_lux'], int)
        item['i_co2'] = safeparse(item['i_co2'], int)
        item['i_pm25'] = safeparse(item['i_pm25'], int)
        item['free'] = item['free'] == '1'
        rooms_new.append(item)
    rooms_new.sort(key=lambda x: x['name'])
    return rooms_new


def get_buildings_headcount():
    data = []
    for building_id, building_name in get_buildings().items():
        building = get_classrooms(building_id)
        count = sum([i['headcount'] for i in building])
        capacity = sum([i['seats'] for i in building])
        data.append(
            {
                'percentage': 100*count//capacity if capacity != 0 else 0,
                'count': count,
                'name': building_name
            }
        )
    return data

