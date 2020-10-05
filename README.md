# ChiMasterBot 迟宝的主人

一个运行于新生QQ群的自动机器人

## 功能概述

- 智能答疑，灵感来源于 [Chi-QQBot](https://github.com/Chi-Task-Force/Chi-QQBot)
- 自动学习，抄袭 [Chi-QQBot](https://github.com/Chi-Task-Force/Chi-QQBot) 的答疑素材
- 查询食堂、图书馆占用率情况
- 基于[迟先生语料库](https://github.com/Chi-Task-Force/Chi-Corpus)进行“卖弱”
- 随机调取中文词语、成语，数据来自 [chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua)
- 随机调取唐诗、宋词，数据来自 [chinese-poetry-zhCN](https://github.com/chinese-poetry/chinese-poetry-zhCN) 和 [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) 
- 随机抓取[人民网](http://www.people.com.cn/)新闻标题
- 消息撤回警告
- 按关键词自动撤回消息与禁言
- 复读打断
- 基于命令的增删答疑数据
- 使用答案之书素材“做决定“
- 自助戳人

## 安装与运行

1. 下载并安装 Python，下载地址：https://www.python.org/downloads/

2. 安装有关依赖

   ```shell
   pip install -r requirements.txt
   ```

3. 下载并运行 go-cqhttp，下载地址：https://github.com/Mrs4s/go-cqhttp/releases

4. 首次运行后， go-cqhttp 将自动生成配置文件，需对配置文件进行一些修改

   - 将 `uin` 填写为 QQ 号（为防止意外，不建议使用个人常用 QQ 号）
   - 将 `password` 填写为 QQ 密码
   - 将 `http_config` 下的 `enable` 修改为 `false`
   - 将 `ws_config` 下的 `enable` 修改为 `false`
   - 将 `ws_reverse_servers` 下的 `enable` 修改为 `true`
   - 将 `ws_reverse_servers` 下的 `reverse_url`、`reverse_api_url`、`reverse_event_url` 均修改为 `ws://localhost:52311/ws`
   - 将 `post_message_format` 修改为 `array`

5. 再次运行 go-cqhttp ，应当可以正常登录，或按步骤进行 `QQ设备锁` 验证

6. 运行本程序

   ```shell
   python main.py
   ```

7. 应当可以工作

