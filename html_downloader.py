'''
@Description: 下载器
@Author: Steven
@Date: 2018-09-18 10:15:44
@LastEditors  : Steven
@LastEditTime : 2020-01-09 10:34:35
'''
# -*- coding: utf-8 -*-
# Created on 2018年3月9日
# @author: Administrator
import requests # type: ignore
import time
import random

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,th-TH;q=0.8,th;q=0.7,zh-CN;q=0.6,zh-TW;q=0.5,zh;q=0.4',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'cookie': 'PHPSESSID=1234567890'
}


class HtmlDownloader:
    def download(self, url: str) -> str:
        if url is None:
            return None

        # 添加随机延迟
        time.sleep(random.uniform(1, 3))

        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                return None
            # print(resp.text)
            # save_path = f"html_data/{url.split('/')[-1]}.html"
            # with open(save_path, 'w', encoding='utf-8') as f:
            #     f.write(resp.text)
            return resp.text
        except requests.Timeout:
            print(f"请求超时: {url}")
            return None
        except requests.RequestException as e:
            print(f"请求失败: {url}, 错误: {e}")
            return None


if __name__ == "__main__":
    downloader = HtmlDownloader()
    print(downloader.download('https://www.dhgate.com/w/women+dress/0.html'))
