# 百度爬虫配置文件

import os

project_dir = os.path.dirname(os.path.abspath(__file__))
# 结果数据存储目录
BAIDU_DATA_DIR_PATH = project_dir + '/baidu_data/'
# 百度真相结果数据文件
BAIDU_ZHENXIANG_FILE = 'baidu_zhengxiang.txt'
# 百度真相URL
BAIDU_ZHENGXIANG_URL = 'https://zhidao.baidu.com/liuyan/list'

# PKL文件存储目录
BAIDU_PKL_DIR_PATH = project_dir + '/baidu_pkl/'
# 百度真相PKL文件
BAIDU_ZHENXIANG_PKL_FILE = 'baidu_zhenxiang.pkl'

