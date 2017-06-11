# -*- coding: utf-8 -*-
# file: main.py
# author: huachengyu
# time: 09/06/2017 10:10 AM
# Copyright 2017 huachengyu. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------
"""
递归爬去百度真相QA数据,真相数据相当于标注好的常识类的领域数据
"""

import csv
import sys
import pickle

import requests
from lxml import etree

from baidu_scraper.baidu_config import *


def write_row(rows):
    # 以追加方式写入,使用\2分割符分割
    with open(BAIDU_DATA_DIR_PATH + BAIDU_ZHENXIANG_FILE, 'a', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\2')
        writer.writerows(rows)


def start_scraper(cid, pn):
    # 构造爬取URL
    start_url = BAIDU_ZHENGXIANG_URL + '?cid=%s&rn=20&pn=%s' % (cid, pn)
    print("scraper url is {}".format(start_url))

    try:
        # 获取列表LIST内容
        zx_start_html = requests.get(start_url).content
        start_selector = etree.HTML(zx_start_html)
        second_url_list = start_selector.xpath('//ul[@class="wgt-list"]/li/dl')
        if len(second_url_list) == 0:
            print("list is null, end!")
            return

        for s_url in second_url_list:
            try:
                # 获取详情页
                second_url = s_url.xpath('dt/h3/a/@href')
                detail_url = 'https://zhidao.baidu.com' + second_url[0]
                detail_html = requests.get(detail_url).content
                detail_selector = etree.HTML(detail_html)
                # 获取QA问答对
                q_list = detail_selector.xpath('//span[@class="f-28 v-middle"]/text()')
                a_list = detail_selector.xpath('//div[@class="abstract"]/text()')
                q = ''
                a = ''
                # 不同详情页解析情况不同
                if len(q_list) > 0 and len(a_list) > 0:
                    q = q_list[0]
                    a = a_list[1].replace('\n', '')
                elif len(q_list) > 0 and len(a_list) == 0:
                    q = q_list[0]
                    a_list_black = detail_selector.xpath('//div[@id="j-reasoning-detail-content"]/p/strong//text()')
                    if len(a_list_black) == 0:
                        # 没有匹配答案,下一个问题继续
                        continue
                    for a_black in a_list_black:
                        a += a_black

                # 获取问答时间
                qa_date = s_url.xpath('dd/span[@class="time"]/text()')

                # 拼接输出文件数组结构
                if a != '' and q != '' and len(qa_date) > 0:
                    new_row = [1] * 3
                    new_row[0] = q
                    new_row[1] = a
                    new_row[2] = qa_date[0]
                    list = []
                    list.append(new_row)
                    # 输出文件
                    write_row(list)
            except KeyboardInterrupt:
                # 键盘打断,则保留现场,以便下次继续
                print("KeyboardInterrupt : save baidu_zhenxiang.pkl.")
                with open(BAIDU_PKL_DIR_PATH + BAIDU_ZHENXIANG_PKL_FILE, 'wb') as f:
                    cidPnDict = {}
                    cidPnDict['cid'] = cid
                    cidPnDict['pn'] = pn
                    pickle.dump(cidPnDict, f)
            except Exception as e:
                print(e)
                continue
    except KeyboardInterrupt:
        # 键盘打断,则保留现场,以便下次继续
        print("KeyboardInterrupt : save baidu_zhenxiang.pkl.")
        with open(BAIDU_PKL_DIR_PATH + BAIDU_ZHENXIANG_PKL_FILE, 'wb') as f:
            cidPnDict = {}
            cidPnDict['cid'] = cid
            cidPnDict['pn'] = pn
            pickle.dump(cidPnDict, f)
    except Exception as e:
        print(e)
        pass

    # 迭代
    pn += 20
    start_scraper(cid, pn)


if __name__ == '__main__':
    # 命令传入参数,若没有则默认
    if len(sys.argv) < 3:
        # 查询之前是否手动中断,进行断点爬取
        if os.path.exists(BAIDU_PKL_DIR_PATH + BAIDU_ZHENXIANG_PKL_FILE):
            with open(BAIDU_PKL_DIR_PATH + BAIDU_ZHENXIANG_PKL_FILE, 'rb') as f:
                cidPnDict = pickle.load(f)
                cid = cidPnDict['cid']
                pn = cidPnDict['pn']
                print('load baidu_zhenxiang.pkl, use store param. cid = %s, pn = %s' % (cid, pn))
                start_scraper(cid, pn)
        else:
            # 没有PKL则从0开始
            # cid : 0 : 全部分类
            # pn : 0 : 第0页开始
            print('use default param. cid = 0, pn =0')
            start_scraper(0, 0)
    else:
        # sys.argv[1]:cid : 分类
        # sys.argv[1]:pn : 页码
        start_scraper(sys.argv[1], sys.argv[1])
