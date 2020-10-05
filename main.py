# python
import json
import logging
import random
import re
from datetime import datetime
from pathlib import Path
from string import punctuation, whitespace
from sys import stdout
from time import time, sleep
from typing import List
import asyncio

from aiocqhttp import CQHttp, Event
from rapidfuzz import process

from canteen import get_canteen_msg, get_library_msg, get_news_msg
from dictionary import get_cheng_yu, get_ci_yu, get_tang_shi, get_song_ci

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(stream=stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
log.addHandler(console_handler)

file_handler = logging.FileHandler(filename='log.csv')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s, %(levelname)s, %(name)s, %(message)s'))
log.addHandler(file_handler)

QUESTIONS: dict = {}
QUESTIONS_KEY: dict = {}
ADMINS: list = []
HATE_LIST = {}
RECALL_RECORD = {}

CHI_BOT = 1486024403
IDIOT = 2780065314

CORPUS: List[str] = []
TRIGGER: List[str] = []
REFUSE: List[str] = []
BOOK: List[str] = []

COMMAND_REGEX = re.compile(r'问\s*(\S+)')

Repeat_Monitor = {'repeating_count': 0, 'last_message': ''}

wait_chi_answer = None


class Config:
    repeat_prob: float
    repeat_delay: float
    weak_prob: float
    weak_delay: float
    battle_prob: float
    recall_react_delay: float

    def __init__(self,
                 repeat_prob: float,
                 repeat_delay: float,
                 weak_prob: float,
                 weak_delay: float,
                 battle_prob: float,
                 recall_react_prob: float,
                 recall_react_delay: float):
        self.repeat_prob = repeat_prob
        self.repeat_delay = repeat_delay
        self.weak_prob = weak_prob
        self.weak_delay = weak_delay
        self.battle_prob = battle_prob
        self.recall_react_prob = recall_react_prob
        self.recall_react_delay = recall_react_delay


active_config = Config(
    repeat_prob=0,
    repeat_delay=3,
    weak_prob=0,
    weak_delay=1.2,
    battle_prob=0,
    recall_react_prob=0.2,
    recall_react_delay=0.5
)

night_config = Config(
    repeat_prob=0,
    repeat_delay=4,
    weak_prob=0,
    weak_delay=1.2,
    battle_prob=0,
    recall_react_prob=0.2,
    recall_react_delay=0.5
)

daylight_config = Config(
    repeat_prob=0,
    repeat_delay=4,
    weak_prob=0,
    weak_delay=4,
    battle_prob=0,
    recall_react_prob=0.2,
    recall_react_delay=1
)

bot = CQHttp()


async def answer_all(event: Event):
    await bot.send(
        event,
        message=f'我能够回答的问题好多呢，我随便说十个：',
        auto_escape=True
    )

    await asyncio.sleep(0.8)

    await bot.send(
        event,
        message='、'.join(random.sample(list(QUESTIONS), 10)),
        auto_escape=True
    )

    await asyncio.sleep(0.8)

    await bot.send(
        event,
        message=f'多不多？如果喜欢我，就加我为好友吧！',
        auto_escape=True
    )

    # reply_msg = f"我能够回答的问题好多呢！"：{'、'.join(random(QUESTIONS)}。\n @ 我问个问题吧，需要以 “问”开头！"
    return None  # {'reply': reply_msg}


def answer_book(event: Event):
    return {'reply': f"[CQ:reply,id={event['message_id']}] {random.choice(BOOK)}"}


async def answer_weakness(event: Event):
    say=random.choice(CORPUS)
    await bot.send(event,say)
    return {'reply': f'[CQ:tts,text={say}啊啊啊]'}


def answer_battle():
    return {'reply': random.choice(TRIGGER) + f' [CQ:at,qq={CHI_BOT}]'}


def answer_repeat(event: Event):
    return {'reply': event.raw_message.replace(at(event.self_id), '')}


def answer_video():
    return None


def answer_reply(message, reply_to=None, mention=None):
    if reply_to:
        reply_to = f'[CQ:reply,id={reply_to}]'
    else:
        reply_to = ''
    if mention:
        mention = at(mention)+'\n'
    else:
        mention = ''

    message = message.strip()

    msg = reply_to+mention+message
    log.info(f'message replied: {msg}')
    sleep(random.randint(1200, 1900)/1000)
    return {'reply': reply_to+mention+message}


def at(qq):
    return f'[CQ:at,qq={qq}]'


def answer_enlightenment():
    return {'reply': f'[CQ:image,file=1cbb384da02520732b3a1037b8ac559b.image]'}


NEXT = None


async def card_check(event: Event):
    if event['group_id'] != 670021746:
        return
    card = event['sender']['card'].strip()
    if not re.match(r'\A[0-9]+?[\-\+ _].+?[\-\+\ _].+?\Z', card):
        pass
        # await bot.send_private_msg(
        #     user_id=event['user_id'],
        #     message=f'你的名片为{card}，不符合条件。请以【本科入学年份-专业-名字】命名，谢谢！'
        # )


@ bot.on_notice('group_increase')
async def _(event: Event):
    # info = await bot.get_group_member_info(group_id=event.group_id,
    #                                        user_id=event.user_id)
    # nickname = info['nickname']
    # name = nickname if nickname else '新人'
    return
    await bot.send(event,
                   message=f'我是热心机器人！@我，探索我的更多功能！',
                   at_sender=True,
                   auto_escape=True)

CHECK_SENDER_CARD = False


@ bot.on_message('private')
async def _(event: Event):
    await asyncio.sleep(0.8)
    await bot.send(event,
                   message=f'你刚才说了：{event.raw_message}',
                   at_sender=True,
                   auto_escape=True)

    await asyncio.sleep(0.8)
    await privite_hello(event.user_id)


async def privite_hello(user_id):
    # user_info = await bot.get_stranger_info(
    #     user_id=user_id,
    #     no_cache=True
    # )

    # his_name = user_info['nickname']

    await asyncio.sleep(0.8)
    await bot.send_private_msg(
        user_id=user_id,
        message=f'嗨！你好啊。我现在还没有任何功能呢。你有什么建议吗？',
        auto_escape=True
    )


@ bot.on_message('group')
async def _(event: Event):
    global wait_chi_answer
    global QUESTIONS

    log.info(f'new measage:【{event.raw_message}】')

    if CHECK_SENDER_CARD:
        await card_check(event)

    # log.debug(
    #     f'message received event! event:{event}')

    messages = list(filter(lambda m: m['type'] == 'text', event.message))

    if messages:
        message_text = ' '.join([i['data']['text'].strip()
                                 for i in messages])
    else:
        message_text = None

    if type(message_text) == str and message_text == Repeat_Monitor['last_message']:
        Repeat_Monitor['repeating_count'] += 1
    else:
        Repeat_Monitor['last_message'] = message_text
        Repeat_Monitor['repeating_count'] = 1

    if Repeat_Monitor['repeating_count'] == 6:
        Repeat_Monitor['repeating_count'] = 0
        return answer_enlightenment()

    # if Repeat_Monitor['repeating_count'] > 1:
    #     return None

    # 迟宝发的消息
    if event.user_id == CHI_BOT:
        started_flag = False
        if wait_chi_answer:
            # 临时加的
            cmd_q = wait_chi_answer
            wait_chi_answer = None
            cmd_a = '【'.join(event.raw_message.split('【')[:-1])
            if cmd_q in QUESTIONS:
                if not '【' in event.raw_message:
                    del QUESTIONS[cmd_q]
                    return answer_reply(
                        f'答案已删除'
                    )
                if type(QUESTIONS[cmd_q]) == str:
                    QUESTIONS[cmd_q] = {}
                    QUESTIONS[cmd_q]['alias'] = [cmd_q]
                QUESTIONS[cmd_q]['answer'] = cmd_a
                save_questions()
                return answer_reply(
                    f'答案学习成功，问题：《{cmd_q}》，回答：《{cmd_a}》'
                )
            else:
                return answer_reply(
                    f'问题尚不存在'
                )
            # 一会一定删掉哈
        return None

        message_content = [line for line in message_text.split(
            '\n') if line.count('、') > 30]
        if message_content:
            questions = message_content[0].split('、')
            new = []
            for i in questions:
                i = i.strip()
                if i == '':
                    continue
                if i not in QUESTIONS:
                    QUESTIONS[i] = i
                    new.append(i)
            save_questions()
            if new:
                return answer_reply(
                    f'新补充了问题：{"、".join(new)}'
                )
            else:
                return answer_reply(
                    f'没加新的问题。'
                )

    if at(IDIOT) in event.raw_message:
        return None

    if at(event.self_id) in event.raw_message or event.raw_message.startswith('@主人') or event.raw_message.startswith('问 '):
        if event['user_id'] in HATE_LIST:
            if message_text == '对不起':
                del HATE_LIST[event['user_id']]
                return answer_reply('我就知道你还爱我', event['message_id'])
            return answer_reply('[CQ:image,file=a5445a8be0afa913756c574e07fa0757.image]', reply_to=event['message_id'])

    if 1:  # 响应任何消息
        if at(CHI_BOT) in event.raw_message:
            return
        if r'/问号脸' in event.raw_message:
            return

        msg_c = event.raw_message.strip(whitespace).strip()

        msg: str = msg_c.strip(punctuation + whitespace)
        all_at_user = [int(m['data']['qq'])
                       for m in event.message if m['type'] == 'at']

        # msg_c = msg_c.replace('@主人', '').strip()
        # log.info(
        #     f'{event.sender["card"]} call me , he says <{msg}>, raw msg <{event.raw_message}>')

        if msg.startswith('问 '):
            start = time()
            question = COMMAND_REGEX.search(msg).groups()[0]
            if len(question) > 8:
                return None
            (match_choice, score) = process.extractOne(
                question, QUESTIONS_KEY.keys())
            end = time()
            match_choice = QUESTIONS_KEY[match_choice]
            log.info(
                ','.join([str(x) for x in [question, match_choice, '{:.01f}'.format(score)]]))
            if score < 45:
                return answer_reply(f'我可能还不知道，不如问问别人？【@我 all】可以查到我知道的所有问题', event['message_id'], event['user_id'])
            if score < 60:
                return answer_reply(f'不如试着问问[{match_choice}]？', event['message_id'], event['user_id'])
            else:
                if type(QUESTIONS[match_choice]) == str:
                    # 这是chibot知道的问题
                    wait_chi_answer = match_choice
                    return {'reply': f'{at(CHI_BOT)} 问 {match_choice}'}
                else:
                    return answer_reply(QUESTIONS[match_choice]['answer']+f'【{match_choice}】', reply_to=event['message_id'])

        if (msg.startswith('主人，') or msg.startswith('主人主人，')) and (msg.endswith('？')):
            return answer_book(event)

        if msg == 'all':
            await answer_all(event)
            return

        help_msg = str('问……：向@ChiBot进行合理提问，例：问水源\n'
                       '主人，……？：通过马纳姆效应解决历史难题，例：主人，你看我帅吗？\n'
                       '卖弱：基于迟先生语录展开卖弱\n'
                       '谢谢：回答不客气\n'
                       '对不起：回答没关系\n'
                       '-f, --faq, 维护：维护智能解答列表\n'
                       '-c, --canteen, 食堂：查询食堂当前就餐人数和剩余承载力\n'
                       '-l, --library, 图书馆：查询图书馆当前在馆人数和剩余承载力\n'
                       '-n, --news, 新闻：查询最新新闻\n'
                       'all：查询问答模式支持的所有命令，同-f q\n'
                       '-m, --mute, 静音, 闭嘴：进入静音模式\n'
                       '-w, --word, 词语：来一条词语\n'
                       '-i, --idiom, 成语：来一条成语\n'
                       '-p, --poetry, 唐诗：来一首唐诗\n'
                       '-s, --songci, 宋词：来一首宋词\n'
                       '-v, --version, 版本：显示当前版本\n'
                       '-h, --help, 帮助：显示我的帮助\n'
                       '-a, --about, 关于：关于我\n'
                       '-q, --quit, 退出, 走开：被机器人忽视，道歉后可恢复')
        if '谢谢' == msg_c:
            return answer_reply('不客气（虽然可能不是对我说的，但是这种简单的回复，我可以代劳）')
        if '对不起' == msg_c:
            return answer_reply('没关系（虽然可能不是对我说的，但是这种简单的回复，我可以代劳）')
        if '卖弱' == msg_c:
            ds= await answer_weakness(event)
            return ds
        if start_in(msg_c.strip(), ['维护', '-f', '--faq']):
            msg_admin_list = f"管理员列表：{'、'.join([str(x) for x in ADMINS])}，请联系管理员索要管理员权限。"
            faq_help = str(
                '维护智能解答列表\n'
                '命令原型：@我 --faq\n'
                '参数：'
                'add：添加问题，例：add 这个问题 那个答案\n'
                'edit：修改答案，例：edit 这个问题 这个答案\n'
                'amend：追加答案，例：amend 这个问题 第二个答案\n'
                'del：删除问题，例：del 这个问题\n'
                'addalias：添加别名，例：addalias jAccount 甲亢\n'
                'show：显示当前所有问题，例：show q或show ans或show alias或show chiknow\n'
                'auth：授权用户维护列表，例：auth @某人\n'
                'admin：显示授权用户列表，例：admin\n'
                'help：显示帮助\n'
            )
            cmd = ' '.join(msg_c.split(' ')[1:]).strip()
            cmd_0 = cmd.split(' ')[0].strip()
            log.info(f'faq command:{cmd_0}')

            if cmd_0 == 'add':
                if event['user_id'] not in ADMINS:
                    return answer_reply('无权操作，'+msg_admin_list, reply_to=event['message_id'])
                cmd2 = event.raw_message[event.raw_message.find(
                    cmd_0)+len(cmd_0):].strip()
                cmd_q = cmd2.split(' ')[0].strip()
                cmd_a = ' '.join(cmd2.split(' ')[1:]).strip()
                if 'CQ:image' in cmd_q:
                    return answer_reply(
                        f'问题标题内带有图片，请修改后再添加'
                    )
                if cmd_q not in QUESTIONS:
                    QUESTIONS[cmd_q] = {}
                    QUESTIONS[cmd_q]['answer'] = cmd_a
                    QUESTIONS[cmd_q]['alias'] = [cmd_q]
                    save_questions()
                    return answer_reply(
                        f'问题添加成功，问题：《{cmd_q}》，回答：《{cmd_a}》'
                    )
                else:
                    return answer_reply(
                        f'问题已存在，请进行更新'
                    )
            elif cmd_0 == 'addalias':
                if event['user_id'] not in ADMINS:
                    return answer_reply('无权操作，'+msg_admin_list, reply_to=event['message_id'])
                cmd2 = event.raw_message[event.raw_message.find(
                    cmd_0)+len(cmd_0):].strip()
                cmd_q = cmd2.split(' ')[0].strip()
                cmd_a = ' '.join(cmd2.split(' ')[1:]).strip()
                if cmd_q in QUESTIONS:
                    if cmd_a not in QUESTIONS[cmd_q]['alias']:
                        QUESTIONS[cmd_q]['alias'].append(cmd_a)
                    save_questions()
                    log.warning(
                        f'question alias【{cmd_q}】 = 【{cmd_a}】added!')
                    return answer_reply(
                        f"问题别名添加成功，问题：《{cmd_q}》，别名：《{'、'.join(QUESTIONS[cmd_q]['alias'])}》"
                    )
                else:
                    return answer_reply(
                        f'问题尚不存在，请先添加'
                    )
            elif cmd.startswith('show'):
                cmd2 = ' '.join(cmd.split(' ')[1:]).strip()
                cmd_para1 = cmd2.split(' ')[0].strip()

                if cmd_para1 == 'ans':
                    if event['user_id'] not in ADMINS:
                        return answer_reply('无权操作，'+msg_admin_list, reply_to=event['message_id'])
                    ans = '\n'.join(
                        [
                            f"问：【{k}？】\n答：【{v['answer']}】\n"
                            for k, v in QUESTIONS.items()
                            if type(v) == dict
                        ]
                    )
                elif cmd_para1 == 'chiknow':
                    ans = 'ChiBot知道而我不知道的问题：'
                    ans += '、'.join(
                        [
                            f"{k}"
                            for k, v in QUESTIONS.items()
                            if type(v) != dict
                        ]
                    )
                elif cmd_para1 == 'alias':
                    ans = '问题及其别名列表：'
                    ans += '、'.join(
                        [
                            f"{k}:[{','.join(v['alias'])}]"
                            for k, v in QUESTIONS.items()
                            if type(v) == dict
                        ]
                    )
                else:
                    ans = '、'.join(
                        [
                            f"{k}"
                            for k, v in QUESTIONS.items()
                        ]
                    )
                return answer_reply(ans, mention=event.user_id)
            elif cmd.startswith('del'):
                if event['user_id'] not in ADMINS:
                    return answer_reply('无权操作，'+msg_admin_list, reply_to=event['message_id'])
                cmd2 = ' '.join(cmd.split(' ')[1:]).strip()
                cmd_q = cmd2.split(' ')[0].strip()

                if cmd_q in QUESTIONS:
                    del QUESTIONS[cmd_q]
                    save_questions()
                    log.warning(f'question 【{cmd_q}】 deleted!')
                    return answer_reply(
                        f'问题《{cmd_q}》删除成功'
                    )
                else:
                    return answer_reply(
                        f'问题不存在，无法删除'
                    )
            elif cmd_0 == 'edit':
                if event['user_id'] not in ADMINS:
                    return answer_reply('无权操作，'+msg_admin_list, reply_to=event['message_id'])
                cmd2 = event.raw_message[event.raw_message.find(
                    cmd_0)+len(cmd_0):].strip()
                cmd_q = cmd2.split(' ')[0].strip()
                cmd_a = ' '.join(cmd2.split(' ')[1:]).strip()
                if cmd_q in QUESTIONS:
                    if type(QUESTIONS[cmd_q]) == str:
                        QUESTIONS[cmd_q] = {}
                        QUESTIONS[cmd_q]['alias'] = [cmd_q]
                    old_ans = QUESTIONS[cmd_q]['answer']
                    QUESTIONS[cmd_q]['answer'] = cmd_a
                    save_questions()
                    log.warning(
                        f'question 【{cmd_q}】 answer updated【{old_ans}】->【{cmd_a}】')
                    return answer_reply(
                        f'回答更新成功，问题：《{cmd_q}》，新回答：《{cmd_a}》'
                    )
                else:
                    return answer_reply(
                        f'问题尚不存在，请先添加',
                        mention=event.user_id
                    )
            elif cmd_0 == 'amend':
                if event['user_id'] not in ADMINS:
                    return answer_reply('无权操作，'+msg_admin_list, reply_to=event['message_id'])
                cmd2 = event.raw_message[event.raw_message.find(
                    cmd_0)+len(cmd_0):].strip()
                cmd_q = cmd2.split(' ')[0].strip()
                cmd_a = ' '.join(cmd2.split(' ')[1:]).strip()
                if cmd_q in QUESTIONS:
                    if type(QUESTIONS[cmd_q]) == str:
                        QUESTIONS[cmd_q] = {}
                        QUESTIONS[cmd_q]['alias'] = [cmd_q]
                    old_ans = QUESTIONS[cmd_q]['answer']
                    QUESTIONS[cmd_q]['answer'] += cmd_a
                    cmd_a = QUESTIONS[cmd_q]['answer']
                    save_questions()
                    log.warning(
                        f'question 【{cmd_q}】 answer amended 【{old_ans}】 -> 【{cmd_a}】')
                    return answer_reply(
                        f'回答补充成功，问题：《{cmd_q}》，新回答：《{cmd_a}》',
                        mention=event.user_id
                    )
                else:
                    return answer_reply(
                        f'问题【{cmd_q}】尚不存在，请先添加',
                        mention=event.user_id
                    )
            elif cmd.startswith('auth'):
                if event['user_id'] not in ADMINS:
                    return answer_reply('无权操作，'+msg_admin_list, reply_to=event['message_id'])
                cmd2 = ' '.join(cmd.split(' ')[1:]).strip()

                para_qqs = all_at_user
                msg = ''
                if len(para_qqs):
                    for para_qq in para_qqs:
                        if para_qq not in ADMINS:
                            ADMINS.append(para_qq)
                            save_admin()
                        log.warning(f'authorized user {para_qq} added!')
                        msg += f'用户授权成功，{at(para_qq)}（QQ号{para_qq}）现在已经能够维护智能解答列表。\n'
                    return answer_reply(
                        msg +
                        f"当前管理员共{len(ADMINS)}人"
                    )
                else:
                    return answer_reply('请艾特一个或多个待授权用户', reply_to=event['message_id'])
            elif cmd.startswith('admin'):
                return answer_reply(msg_admin_list, reply_to=event['message_id'])
            else:
                return answer_reply(faq_help, mention=event.user_id)
        if msg_c in ['食堂', '-c', '--canteen']:
            return answer_reply(get_canteen_msg())
        if msg_c in ['图书馆', '-l', '--library']:
            return answer_reply(get_library_msg())
        if msg_c in ['词语', '-w', '--word']:
            return answer_reply(get_ci_yu())
        if msg_c in ['成语', '-i', '--idiom']:
            return answer_reply(get_cheng_yu())
        if msg_c in ['唐诗', '-p', '--poetry']:
            return answer_reply(get_tang_shi())
        if msg_c in ['宋词', '-s', '--songci']:
            return answer_reply(get_song_ci())
        if msg_c in ['新闻', '-n', '--news']:
            return answer_reply(get_news_msg())
        if msg_c in ['帮助', '-h', '--help']:
            return answer_reply('\n'+help_msg)
        if msg_c in ['版本', '-v', '--version']:
            return answer_reply('您使用已经是最新版了！[CQ:face,id=66][CQ:face,id=66][CQ:face,id=66]')
        if msg_c in ['关于', '-a', '--about']:
            about_msg = str(
                f'机器人源代码来自：https://github.com/LuminousXLB/TaraBot，原作者小笼包。'
                f'由人参果修改并运营。'
                f'卖弱素材由迟先生编纂（有关更多关于迟先生的个人信息，可以问我）；'
                f'历史难题答案素材来源于《答案之书》；'
                f'答疑素材由ddl编写，目前可由管理员通过交互命令进行完善；'
                f'实时信息查询来自于相应各开放接口。'
            )
            return answer_reply(about_msg)
        if msg_c in ['退出', '走开', '-q', '--quit']:
            HATE_LIST[event['user_id']] = True
            return answer_reply('[CQ:image,file=a5445a8be0afa913756c574e07fa0757.image]', reply_to=event['message_id'])
        if msg_c in ['静音', '闭嘴', '-m', '--mute']:
            return answer_reply('让我静音的办法：\n[CQ:image,file=a77115bfe33c4e81fbeaf6a477bf5424.image]')
        if msg_c in ['离开']:
            return answer_reply('''[CQ:xml,data=<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID="1" templateID="-1" action="web" brief="公安局已离开" sourceMsgId="0" url="" flag="0" adverSign="0" multiMsgFlag="0"><item layout="2" advertiser_id="0" aid="0"><picture cover="http://p.qpic.cn/qqshare/0/0bbf35a703b29c86d989636509d5d1ca/0" w="0" h="0" /><title>公安局已离开该群</title><summary>公安局已停止监控聊天</summary></item><source name="中国刑警大队已离开，请自由聊天" icon="" action="" appid="0" /></msg>]''')
        if msg_c in ['进入']:
            return answer_reply('''[CQ:xml,data=<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID="1" templateID="-1" action="web" brief="公安局已介入" sourceMsgId="0" url="" flag="0" adverSign="0" multiMsgFlag="0"><item layout="2" advertiser_id="0" aid="0"><picture cover="http://p.qpic.cn/qqshare/0/0bbf35a703b29c86d989636509d5d1ca/0" w="0" h="0" /><title>公安局已加入该群</title><summary>公安局已开始监控聊天</summary></item><source name="中国刑警大队已介入，请规范聊天" icon="" action="" appid="0" /></msg>]''')
        if msg_c in ['管理员']:
            return None
            return answer_reply('''[CQ:json,data={"app":"com.tencent.autoreply"&#44;"desc":""&#44;"view":"autoreply"&#44;"ver":"0.0.0.1"&#44;"prompt":"新人入群"&#44;"meta":{"metadata":{"title":"本群免费发放管理员身份"&#44;"buttons":&#91;{"slot":1&#44;"action_data":"我现在有管理员权限了！"&#44;"name":"点我获取管理员权限"&#44;"action":"notify"}&#93;&#44;"type":"guest"&#44;"token":"LAcV49xqyE57S17B8ZT6FU7odBveNMYJzux288tBD3c="}}&#44;"config":{"forward":1&#44;"showSender":1}}]''')
        if msg_c in ['试试']:
            return answer_reply('[CQ:video,file=1cccd7f31e56193694f82349844f7246.video]')
        if msg_c in ['语音测试']:
            return answer_reply('[CQ:tts,text=这是一条测试消息]')
        if msg_c in ['主人跟大家问个好']:
            return answer_reply('[CQ:tts,text=你们好啊，我是主人啊啊！]')
        if msg_c == '敏感词':
            await bot.delete_msg(message_id=event['message_id'])
            return None
        if msg_c.startswith('戳'):
            for user in all_at_user:
                await bot.send(event,
                               message=f'[CQ:poke,qq={user}]',
                               at_sender=True,
                               auto_escape=True)
            return
        if msg_c.startswith('网易云 '):
            return answer_reply('''[CQ:xml,data=<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID="2" templateID="1" action="web" brief="&#91;分享&#93; 十年" sourceMsgId="0" url="http://music.163.com/m/song/409650368" flag="0" adverSign="0" multiMsgFlag="0" ><item layout="2"><audio cover="http://p2.music.126.net/g-Qgb9ibk9Wp_0HWra0xQQ==/16636710440565853.jpg?param=90y90" src="https://music.163.com/song/media/outer/url?id=409650368.mp3" /><title>十年</title><summary>黄梦之</summary></item><source name="网易云音乐" icon="https://pic.rmb.bdstatic.com/911423bee2bef937975b29b265d737b3.png" url="http://web.p.qq.com/qqmpmobile/aio/app.html?id=1101079856" action="app" a_actionData="com.netease.cloudmusic" i_actionData="tencent100495085://" appid="100495085" /></msg>]''')

        return None

        return answer_reply('无法识别的指令！\n'
                            '使用参数-h, --help, 帮助，可显示我的帮助\n', mention=event.user_id)

    r = random.random()

    if '[CQ:video' in event.raw_message:
        return answer_video()

    (match_choice, score) = process.extractOne(
        event.raw_message, TRIGGER + CORPUS)
    # log.debug(f'{event.sender["card"]} == 检测卖弱 {config.weak_prob}')
    # log.info(','.join([str(x)
    #                    for x in [event.raw_message, match_choice, score]]))
    # if score > 50 and r < config.weak_prob:
    #     sleep(random.random() * config.weak_delay)
    #     if r < config.battle_prob:
    #         return {'reply': f'{random.choice(TRIGGER)} {at(CHI_BOT)}'}
    #     else:
    #         return answer_weakness()

    # log.debug(f'{event.sender["card"]} == 随机复读 {config.repeat_prob}')
    # if r < config.repeat_prob:
    #     sleep(random.random() * config.repeat_delay)
    #     return answer_repeat(event)

    log.info(f'no action.')


@ bot.on_notice('group_recall')
async def _(event: Event):
    if event['group_id'] != 670021746:
        return

    # log.debug(
    #     f'message recalled event! event:{event}')

    if event['user_id'] != event['operator_id']:
        return None

    if event['user_id'] not in RECALL_RECORD:
        RECALL_RECORD[event['user_id']] = 0

    time_setting = {6: 3, 7: 20, 8: 60, 9: 360}

    if RECALL_RECORD[event['user_id']] >= 3:
        # await bot.send(event, '请不要撤回消息，首次警告，第六次禁言[CQ:face,id=14]', at_sender=True)

        # await bot.set_group_ban(
        #     group_id=event['group_id'],
        #     user_id=event['user_id'],
        #     duration=60*time_setting[RECALL_RECORD[event['user_id']]]
        # )
        # await bot.send(
        #     event,
        #     '请不要频繁撤回消息！[CQ:face,id=14]',
        #     at_sender=True
        # )

        pass

    RECALL_RECORD[event['user_id']] += 1

    if random.random() < 0:  # active_config.recall_react_prob:
        await bot.send(event, '别撤回了，我全看见了', at_sender=True)
    return None  # answer_reply('别撤回了，我全看见了', mention=event['operator_id'])


@ bot.on_request('friend')
async def _(event):
    # 同意所有加好友请求
    await bot.set_friend_add_request(
        flag=event.flag,
        approve=True,
        remark=''
    )

    log.debug( f'friend request event! event:{event}')

    await asyncio.sleep(0.8)
    await privite_hello(event.user_id)


@ bot.on_request('group')
async def _(event):
    return


def load_corpus():
    global CORPUS, TRIGGER, REFUSE, BOOK
    CORPUS = Path('Chi-Corpus/common.txt').read_text('utf-8').splitlines()
    CORPUS = list(filter(lambda c: '?' not in c, CORPUS))
    TRIGGER = Path('Chi-Corpus/trigger.txt').read_text('utf-8').splitlines()
    REFUSE = Path('Chi-Corpus/refuse.txt').read_text('utf-8').splitlines()
    BOOK = Path('answers.txt').read_text('utf-8').splitlines()


def load_faq_questions():
    global QUESTIONS, QUESTIONS_KEY
    QUESTIONS = json.loads(Path('questions.json').read_text('utf-8'))
    for k, v in QUESTIONS.items():
        if type(v) == dict:
            QUESTIONS_KEY.update({alias: k for alias in v['alias']})
        else:
            QUESTIONS_KEY.update({k: k})


def save_questions():
    Path('questions.json').write_text(
        json.dumps(
            QUESTIONS,
            ensure_ascii=False,
            indent=2
        ),
        'utf-8'
    )
    load_faq_questions()


def load_admin():
    global ADMINS
    ADMINS = json.loads(Path('admins.json').read_text('utf-8'))


def save_admin():
    Path('admins.json').write_text(
        json.dumps(
            ADMINS,
            ensure_ascii=False,
            indent=2
        ),
        'utf-8'
    )


def start_in(msg, leading_list):
    for i in leading_list:
        if msg.startswith(i):
            return True
    return False


if __name__ == '__main__':
    load_faq_questions()
    load_admin()
    load_corpus()
    bot.run(host='localhost', port=52311)
