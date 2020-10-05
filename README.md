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

### 下载本程序

给出两种方法

- 使用 Git 下载（需预先安装 [Git](https://git-scm.com/downloads)）

  1. 在命令行中 clone 本项目，并

     ```shell
     git clone https://github.com/danyang685/ChiMasterBot
     ```

  2. 进入 `ChiMasterBot` 目录，在命令行中 clone `迟先生语料库` 子模块

     ```shell
     git submodule update --init
     ```

- 直接下载

  1. 在本项目的 GitHub 首页中选择绿色的 `Code` 图标，选择 `Download ZIP` ，打包下载本项目，解压为文件夹
  2. 按同样方法下载[迟先生语料库](https://github.com/Chi-Task-Force/Chi-Corpus)，将 `Chi-Corpus-master` 文件夹下的文件解压至本项目文件夹的 `Chi-Corpus` 目录中

### 准备 python 运行环境

1. 下载并安装 Python，下载地址：https://www.python.org/downloads/ ，安装时应勾选 `Add Python 3.x to PATH`

2. 安装有关依赖

   ```shell
   pip install -r requirements.txt
   ```

### 准备 go-cqhttp 运行环境

1. 下载、解压并运行 go-cqhttp，下载地址：https://github.com/Mrs4s/go-cqhttp/releases ，Windows 系统可选择最新版下`windows-amd64` 版本
2. 首次运行后， go-cqhttp 将在当前目录自动生成 `config.json` 配置文件，该文件可用“记事本”或其他文本编辑器打开，需对配置文件进行如下修改

   - 将 `uin` 填写为 QQ 号，直接将 0 改成 QQ 号（为防止意外，不建议使用个人常用 QQ 号）
   - 将 `password` 填写为 QQ 密码，填写在两引号之间
   - 将 `http_config` 下的 `enable` 由 `true` 修改为 `false`
   - 将 `ws_config` 下的 `enable` 由 `true` 修改为 `false`
   - 将 `ws_reverse_servers` 下的 `enable` 由 `false` 修改为 `true`
   - 将 `ws_reverse_servers` 下的 `reverse_url`、`reverse_api_url`、`reverse_event_url` 地址均修改为 `ws://localhost:52311/ws`
   - 将 `post_message_format` 由 `string` 修改为 `array`
   - 将 `web_ui` 下的 `enable` 由 `true` 修改为 `false`
3. 再次运行 go-cqhttp ，可能需要按步骤进行 `QQ设备锁` 验证，随后应当可以正常登录

### 启动

1. 可在 `admins.json` 中`[]`之间填入自己的 QQ 号，作为初始管理员
2. 在命令行中输入 `python main.py` 或直接双击 `main.py` 文件运行本程序

注意：本程序需与 go-cqhttp 共同运行，方可实现功能

