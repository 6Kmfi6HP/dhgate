'''
@Description: 解析器
@Author: Steven
@Date: 2018-09-18 10:15:44
@LastEditors  : Steven
@LastEditTime : 2020-01-09 10:35:21
'''
# -*- coding: utf-8 -*-
# Created on 2018年3月9日
# @author: Administrator
import json
import re
from typing import List
from lxml import etree, html
import requests

from html_downloader import HEADERS


class HtmlParser:
    def _get_new_data(self, page_url: str, tree: etree.Element) -> List:
        try:
            # 获取Next.js的数据脚本
            next_data = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
            if not next_data:
                print("No __NEXT_DATA__ found")
                return []
            
            # 解析JSON数据
            json_data = json.loads(next_data[0])
            
            # 打印JSON结构以便调试
            print("JSON structure:")
            print(json.dumps(json_data.get('props', {}).get('pageProps', {}).get('data', {}), indent=2)[:500])
            
            products = json_data.get('props', {}).get('pageProps', {}).get('data', {}).get('totalProducts', [])
            
            if not products:
                print("No products found in JSON data")
                return []
            
            datas = []
            for product in products:
                try:
                    # 安全地获取价格并处理
                    price_str = product.get('price', '')
                    if price_str and isinstance(price_str, str):
                        price_str = price_str.replace('US $', '')
                        price_parts = price_str.split(' - ')
                        min_price = price_parts[0].strip()
                        max_price = price_parts[1].strip() if len(price_parts) > 1 else min_price
                    else:
                        min_price = '0.00'
                        max_price = '0.00'
                    
                    # 安全地获取最小订购量
                    min_order_str = product.get('minOrder', '1 Piece')
                    min_order_match = re.findall(r'(\d+)', str(min_order_str))
                    min_order_num = min_order_match[0] if min_order_match else '1'
                    
                    product_url = product.get('productDetailUrl', '')
                    detail_data = self._get_product_detail_data(product_url) if product_url else {}
                    
                    data = {
                        'page_url': page_url,
                        'title': product.get('productname', ''),
                        'product_url': product_url.split('#')[0].split('?')[0],
                        'min_price': min_price,
                        'max_price': max_price,
                        'min_order': min_order_num,
                        'order': product.get('recentlysold', '0'),
                        'feedback': str(product.get('feedBackPercent', '0')).replace('%', ''),
                        'seller': product.get('domainname', ''),
                        'store_url': product.get('sellerStoreUrl', '').split('#')[0],
                        **detail_data  # Merge detail data
                    }
                    datas.append(data)
                    # print("data:\n")
                    # print(data)
                    # print("\n")
                   
                    
                except (KeyError, IndexError, ValueError) as e:
                    print(f"Error parsing product: {e}")
                    continue
                    
            return datas
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []
        except Exception as e:
            print(f"Error in _get_new_data: {e}")
            print(f"Tree content: {etree.tostring(tree, pretty_print=True)[:1000]}")
            return []

    def _get_product_detail_data(self, product_url: str) -> dict:
        try:
            # Download the product detail page
            html_content = self._download_html(product_url)
            if not html_content:
                return {}
            
            tree = etree.HTML(html_content)
            
            # Extract content inside the specified div
            description_element = tree.xpath('//div[contains(@class, "prodDesc_decHtml")]/*')
            if description_element:
                # Convert the elements to a string and parse them as HTML
                raw_html = ''.join([etree.tostring(child, encoding='unicode', method='html') for child in description_element])
                parsed_html = html.fromstring(f'<div>{raw_html}</div>')  # Wrap in a div for parsing

                # Remove unnecessary tags and attributes
                for elem in parsed_html.xpath('//*'):
                    # remove not text node
                    # if not elem.text:
                    #     elem.drop_tag()
                    # remove <style>
                    if elem.tag == 'style':
                        elem.drop_tag()
                    # remove <br>
                    if elem.tag == 'br':
                        elem.drop_tag()
                    # remove loading="lazy" in img
                    if elem.tag == 'img' and 'loading' in elem.attrib:
                        del elem.attrib['loading']
                    # Remove style attributes
                    if 'style' in elem.attrib:
                        del elem.attrib['style']

                # Convert back to string, excluding the wrapper div
                cleaned_html = ''.join([html.tostring(child, encoding='unicode', method='html') for child in parsed_html])

            else:
                cleaned_html = ''

            # Extract images
            images = tree.xpath('//ul[contains(@class, "masterMap_smallMapList")]/li/span/img/@src')
            
            # Get the first image
            first_image = images[0] if images else ''
            
            return {
                'first_image': first_image,  # Add first image URL
                'images': ','.join(images),
                'description': cleaned_html.strip() if cleaned_html else ''
            }
        except Exception as e:
            print(f"Error parsing product detail page: {e}")
            return {}

    def _download_html(self, url: str) -> str:
        # This method should be implemented to download HTML content
        # You can use requests or any other library to fetch the HTML
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to download page: {url}")
                return ''
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return ''

    def parse(self, page_url: str, html_cont: str) -> List:
        if page_url is None or html_cont is None:
            return []
            
        tree = etree.HTML(html_cont)
        new_data = self._get_new_data(page_url, tree)
        return new_data

    @staticmethod
    def format_str(text: str) -> str:
        return text.split("html")[0] + "html"
