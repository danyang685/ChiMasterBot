import json
import logging
from pathlib import Path
from util import *
import re
from rapidfuzz import process as fuzz_match

QUESTIONS: dict = {}
QUESTIONS_KEY: dict = {}
ADMINS: list = []

log = logging.getLogger('chimasterbot')

COMMAND_REGEX = re.compile(r'问\s*(\S+)')


def load_faq_questions():
    global QUESTIONS, QUESTIONS_KEY
    if not Path('questions.json').is_file():
        Path('questions.json').write_text(r'{}')
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
    if not Path('admins.json').is_file():
        Path('admins.json').write_text(r'[]')
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


load_faq_questions()
load_admin()


help_text = str(
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


def faq(param_text, operator_id, all_atted_user):
    msg_admin_list = f"管理员列表：{'、'.join([str(x) for x in ADMINS])}，请联系管理员索要管理员权限。"
    unauthorized_text = f'用户【{operator_id}】无权操作，{msg_admin_list}'
    faq_help = help_text

    cmd = param_text.split(' ', 1)[1].strip()

    log.info(f'faq command:{cmd},operator:{operator_id}')

    cmd_0 = cmd.split(' ')[0].strip()

    print(cmd)
    print(cmd_0)

    if cmd_0 == 'add':
        if operator_id not in ADMINS:
            return unauthorized_text
        cmd2 = cmd[cmd.find(cmd_0)+len(cmd_0):].strip()
        cmd_q, cmd_a = [i.strip() for i in cmd2.split(' ', 1)]
        if 'CQ:image' in cmd_q:
            return '问题标题内带有图片，请修改后再添加'
        if not cmd_a:
            return f'请填写回答'
        if cmd_q not in QUESTIONS:
            QUESTIONS[cmd_q] = {}
            QUESTIONS[cmd_q]['answer'] = cmd_a
            QUESTIONS[cmd_q]['alias'] = [cmd_q]
            save_questions()
            return f'问题添加成功，问题：《{cmd_q}》，回答：《{cmd_a}》'
        else:
            return f'问题已存在，请进行更新'
    elif cmd_0 == 'addalias':
        if operator_id not in ADMINS:
            return unauthorized_text
        cmd2 = cmd[cmd.find(cmd_0)+len(cmd_0):].strip()
        cmd_q, cmd_a = [i.strip() for i in cmd2.split(' ', 1)]
        if cmd_q in QUESTIONS:
            if cmd_a not in QUESTIONS[cmd_q]['alias']:
                QUESTIONS[cmd_q]['alias'].append(cmd_a)
            save_questions()
            log.warning(
                f'question alias【{cmd_q}】 = 【{cmd_a}】added!')
            return f"问题别名添加成功，问题：《{cmd_q}》，别名：《{'、'.join(QUESTIONS[cmd_q]['alias'])}》"
        else:
            return f'问题尚不存在，请先添加'
    elif cmd.startswith('show'):
        cmd2 = cmd[cmd.find(cmd_0)+len(cmd_0):].strip()
        cmd_para1 = cmd2.split(' ')[0].strip()

        if cmd_para1 == 'ans':
            if operator_id not in ADMINS:
                return unauthorized_text
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
        return ans
    elif cmd.startswith('del'):
        if operator_id not in ADMINS:
            return unauthorized_text
        cmd2 = ' '.join(cmd.split(' ')[1:]).strip()
        cmd_q = cmd2.split(' ')[0].strip()

        if cmd_q in QUESTIONS:
            del QUESTIONS[cmd_q]
            save_questions()
            log.warning(f'question 【{cmd_q}】 deleted!')
            return f'问题《{cmd_q}》删除成功'
        else:
            return f'问题不存在，无法删除'
    elif cmd_0 == 'edit':
        if operator_id not in ADMINS:
            return unauthorized_text
        cmd2 = cmd[cmd.find(cmd_0)+len(cmd_0):].strip()
        cmd_q, cmd_a = [i.strip() for i in cmd2.split(' ', 1)]
        if not cmd_a:
            return f'请填写回答'
        if cmd_q in QUESTIONS:
            if type(QUESTIONS[cmd_q]) == str:
                QUESTIONS[cmd_q] = {}
                QUESTIONS[cmd_q]['alias'] = [cmd_q]
            old_ans = QUESTIONS[cmd_q]['answer']
            QUESTIONS[cmd_q]['answer'] = cmd_a
            save_questions()
            log.warning(
                f'question 【{cmd_q}】 answer updated【{old_ans}】->【{cmd_a}】')
            return f'回答更新成功，问题：《{cmd_q}》，新回答：《{cmd_a}》'
        else:
            return f'问题【{cmd_q}】尚不存在，请先添加'
    elif cmd_0 == 'amend':
        if operator_id not in ADMINS:
            return unauthorized_text
        cmd2 = cmd[cmd.find(cmd_0)+len(cmd_0):].strip()
        cmd_q, cmd_a = [i.strip() for i in cmd2.split(' ', 1)]
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
            return f'回答补充成功，问题：《{cmd_q}》，新回答：《{cmd_a}》'
        else:
            return f'问题【{cmd_q}】尚不存在，请先添加'
    elif cmd.startswith('auth'):
        if operator_id not in ADMINS:
            return unauthorized_text
        cmd2 = ' '.join(cmd.split(' ')[1:]).strip()

        para_qqs = all_atted_user
        msg = ''
        if len(para_qqs):
            for para_qq in para_qqs:
                if para_qq not in ADMINS:
                    ADMINS.append(para_qq)
                    save_admin()
                log.warning(f'authorized user {para_qq} added!')
                msg += f'用户授权成功，{at(para_qq)}（QQ号{para_qq}）现在已经能够维护智能解答列表。\n'
            return msg + f"当前管理员共{len(ADMINS)}人"
        else:
            return '请艾特一个或多个待授权用户'
    elif cmd.startswith('admin'):
        return msg_admin_list
    else:
        return faq_help


def ask(question):
    question = COMMAND_REGEX.search(question).groups()[0]
    if len(question) > 8:
        return None
    (match_choice, score) = fuzz_match.extractOne(
        question, QUESTIONS_KEY.keys())
    match_choice = QUESTIONS_KEY[match_choice]
    log.info(
        ','.join([str(x) for x in [question, match_choice, '{:.01f}'.format(score)]]))
    if score < 45:
        return f'我可能还不知道，不如问问别人？【@我 all】可以查到我知道的所有问题'
    if score < 60:
        return f'不如试着问问[{match_choice}]？'
    else:
        if type(QUESTIONS[match_choice]) == str:
            # 这是chibot知道的问题
            wait_chi_answer = match_choice
            return f'{at(CHI_BOT)} 问 {match_choice}'
        else:
            return QUESTIONS[match_choice]['answer']+f'【{match_choice}】'
