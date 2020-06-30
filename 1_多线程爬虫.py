import requests
from lxml import etree
from urllib import request
import os
import re
from queue import Queue
import threading
import time
import json



class Procuder(threading.Thread):
    
    def __init__(self,name,page_queue, data_queue, game_queue, g_data_queue,flag):
        super().__init__()
        self.name = name
        self.page_queue = page_queue
        self.data_queue = data_queue
        self.game_queue = game_queue
        self.g_data_queue = g_data_queue
        self.flag = flag
        self.url = 'https://www.3839.com/cdn/comment/view_v2-ac-json-pid-1-fid-{}-p-{}-order-1-htmlsafe-1-urltype-1-audit-1.htm?dm=www.3839.com'
        
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'referer': self.url,
            'X-Requested-With': 'XMLHttpRequest',
        }

        self.url2 = None
        self.headers2 = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'referer': self.url2
        }

    def run(self):
        print('%s线程启动。。。'%self.name)
        '''
        1.从页码队列中取出页码
        2.将页码和url拼接得到url
        3.发送请求，得到相应
        4.将相应内容保存到数据队列中
        '''
        while True:
            try:
                page = self.page_queue.get(True, 5)
                self.url2 = self.game_queue.get(True, 5)
            except:
                self.flag = True
                break
            url = self.url.format(page[1],page[2])
            content = requests.get(url, headers=self.headers)
            content2 = requests.get(self.url2,headers=self.headers2)
            content2.encoding = 'utf-8'
            content3 = content2.text
            s_href = content2.url
            self.data_queue.put(content)
            self.g_data_queue.put([s_href, content3])
    
        print('%s线程结束。。。'%self.name)

    


class Consumer(threading.Thread):
    def __init__(self,name,data_queue, g_data_queue, c_filepath,lock, filepath, flag):
        super().__init__()
        self.name = name
        self.data_queue = data_queue
        self.g_data_queue = g_data_queue
        self.c_filepath = c_filepath
        self.lock = lock
        self.filepath = filepath
        self.flag = flag

    def run(self):
        print('%s---线程启动.......' %self.name)
        '''
        1.从数据队列获取数据
        2.解析
        3.保存文件
        '''
        while True:
            try:
                data = self.data_queue.get(True, 5)
                data2 = self.g_data_queue.get(True, 5)
            except Exception as e:
                self.flag = True
                break
            
            self.parse(data)
            self.parse2(data2)
        print('%s---线程结束.......' %self.name)

    def parse(self, data):
        json1 = data.json()
        content = json1.get('content')
        for x in content:
            comment_id = x.get('id')
            user_id = x.get('uid')
            username = x.get('username')
            # 头像
            portrait = 'https:' + x.get('avatar')
            create_time = x.get('time')
            comment = x.get('comment')
            like_count = x.get('good_num')
            reply_count = x.get('num')


            item = {
                'comment_id':comment_id,
                'user_id':user_id,
                'username':username,
                'portrait':portrait,
                'create_time':create_time,
                'comment':comment,
                'like_count':like_count,
                'reply_count':reply_count,
            }
            string = json.dumps(item,ensure_ascii=False)
            self.lock.acquire()
            self.c_filepath.write(string + '\n')
            self.lock.release()

    def parse2(self, data2):
        s_href = data2[0]
        gameID = s_href.split('/')[-1][:-4:]
        tree = etree.HTML(data2[1])
        logo = tree.xpath('/html/body/div[1]/div[3]/div[1]/div[1]/div[1]/div/img/@src')
        introduce = tree.xpath('/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[1]/div[2]/p[1]/text()')
        score = tree.xpath('/html/body/div[1]/div[3]/div[1]/div[1]/div[1]/div/div[2]/div[1]/p[2]/text()')
        comment_count = tree.xpath('/html/body/div[1]/div[3]/div[1]/div[1]/div[2]/a[2]/span/text()')
        name = tree.xpath('/html/body/div[1]/div[3]/div[1]/div[1]/div[1]/div/div[1]/h1/text()')
        if gameID == '':
            logo, introduce, score, comment_count, name = ['假游戏'], ['假游戏'], ['假游戏'], ['假游戏'], ['假游戏']

        item = {
            '游戏id':gameID,
            '游戏名字':name,
            '游戏图片':'https:'+logo[0],
            '游戏介绍':introduce,
            '评分':score,
            '评论数':comment_count,
        }

        string_game = json.dumps(item,ensure_ascii=False)
        self.filepath.write(string_game + '\n')
        print('游戏结束爬取---%s---' % name[0])

# 得到所有游戏详情链接
def handle_request():
    url = 'https://www.3839.com/top/hot.html'
    headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'referer': 'https://www.3839.com/top/hot.html'
        }

    r = request.Request(url=url,headers=headers)
    content = request.urlopen(r).read().decode('utf8')
    tree = etree.HTML(content)
    game_list = tree.xpath('/html/body/div[1]/div[4]/ul/li/a/@href')
    games = []
    for game in game_list:
        games.append('https:'+game)
    return games



def create_queue():
    page_queue = Queue()
    data_queue = Queue()
    game_queue = Queue()
    g_data_queue = Queue()
    # 向页码队列返回添加待爬的页码
    for game in handle_request():
        game_queue.put(game)
        game_id = game.split('/')[-1][:-4:]
        for x in range(1,11):
            page_queue.put([game,game_id,x])
    return page_queue, data_queue, game_queue, g_data_queue
def main():
    crawl_flag = False
    parse_flag = False
    c_filepath = open('评论11.txt', 'w', encoding='utf8')
    filepath = open('游戏介绍.txt', 'w', encoding='utf8')
   
    lock = threading.Lock()
    # 创建4个队列  页码 评论数据 游戏队列  游戏详情队列
    page_queue, data_queue, game_queue, g_data_queue = create_queue()
    # 保存创建的线程
    t_craw_list = []
    t_parse_list = []
    #创建采集线程并启动
    crawl_name_list = ['采集线程1','采集线程2','采集线程3']
    for crawl_name in crawl_name_list:
        t_craw = Procuder(crawl_name, page_queue, data_queue, game_queue, g_data_queue, crawl_flag)
        t_craw_list.append(t_craw)
        t_craw.start()

    #创建解析线程并启动
    parse_name_list = ['解析线程1','解析线程2','解析线程3']
    for parse_name in parse_name_list:
        t_parse = Consumer(parse_name,data_queue, g_data_queue, c_filepath,lock, filepath, parse_flag)
        t_parse_list.append(t_parse)
        t_parse.start()

    
    # 先判断游戏队列是否为空
    while True:
        if t_craw.flag:
            break
    

    time.sleep(3)
    while True:
        if t_parse.flag:
            break

    
    # 让主线程等待每一个线程
    for t_craw in t_craw_list:
        t_craw.join()
    for t_parse in t_parse_list:
        t_parse.join()
    c_filepath.close()
    print('主线程-子线程全部结束')
    
if __name__ == "__main__":
    main()


