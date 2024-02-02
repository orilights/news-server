import json, os
from datetime import datetime

from flask import Flask, request
from flask_cors import CORS
from flask_compress import Compress
import requests

API_URL = 'https://content-static.mihoyo.com/content/ysCn/getContentList?pageSize={pageSize}&pageNum={pageNum}&channelId=10'
CACHE_FILE = './data/cache.json'

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
compress = Compress(app)


def get_news_count():
    res = requests.get(API_URL.format(pageSize=5, pageNum=1))
    if res.ok and res.json()['retcode'] == 0:
        return res.json()['data']['total']
    else:
        return None


def read_cache():
    if os.path.exists(CACHE_FILE):
        return json.load(open(CACHE_FILE, mode='r', encoding='utf-8'))
    else:
        return None


def write_cache(data):
    if os.path.exists(CACHE_FILE):
        updateTime = json.load(open(CACHE_FILE, mode='r',
                                    encoding='utf-8'))['updateTime']
        updateDate = datetime.fromtimestamp(updateTime).strftime('%Y-%m-%d')
        os.rename(CACHE_FILE, f'{CACHE_FILE}.{updateDate}.bak')
    json.dump(data,
              open(CACHE_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False)


def get_news_data():
    print('获取最新数据')
    news_count = get_news_count()
    res = requests.get(API_URL.format(pageSize=news_count, pageNum=1))
    if res.ok and res.json()['retcode'] == 0:
        return {
            'updateTime': int(datetime.now().timestamp()),
            'newsCount': news_count,
            'newsData': res.json()['data']['list']
        }
    else:
        return None


@app.route('/news', methods=['GET'])
def get_news():
    query = request.args
    force_refresh = query.get('force_refresh', '0') == '1'
    if force_refresh:
        data = get_news_data()
        if data is None:
            return {'code': 1, 'msg': '获取数据失败'}

        write_cache(data)
    else:
        data = read_cache()
        if data is None:
            data = get_news_data()
            if data:
                write_cache(data)
        if data is None:
            return {'code': 1, 'msg': '获取数据失败'}

        if data['updateTime'] + 3600 < int(datetime.now().timestamp()):
            data = get_news_data()
            if data is None:
                return {'code': 1, 'msg': '获取数据失败'}
            write_cache(data)
    return {
        'code': 0,
        'updateTime': data['updateTime'],
        'newsCount': data['newsCount'],
        'newsData': data['newsData']
    }


if __name__ == '__main__':
    app.run('0.0.0.0', port=3000, debug=True)
