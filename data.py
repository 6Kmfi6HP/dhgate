import re
from bs4 import BeautifulSoup
from typing import Dict, List
import requests
from html_downloader import HEADERS


def get_html_content(source: str) -> str:
    """从文件或URL获取HTML内容"""
    if source.startswith(('http://', 'https://')):
        response = requests.get(source, headers=HEADERS)
        response.raise_for_status()  # 检查请求是否成功
        return response.text
    else:
        with open(source, 'r', encoding='utf-8') as file:
            return file.read()

def extract_json_from_script(text: str) -> List[Dict]:
    """提取JavaScript中的JSON数据"""
    # 匹配形如 self.__next_f.push([1,"43:{...}"\n]) 的模式
    pattern = r'self\.__next_f\.push\(\[\d+,"[^"]*?({.*?})"'
    matches = re.findall(pattern, text)
    
    result = []
    for match in matches:
        # 处理转义字符
        json_str = match.encode().decode('unicode_escape')
        try:
            # 这里可以使用json.loads(json_str)处理数据
            result.append(json_str)
        except Exception as e:
            print(f"解析JSON失败: {e}")
    
    return result

def extract_sku_data(source: str) -> List[Dict]:
    # 获取HTML内容（修改这部分）
    try:
        html_content = get_html_content(source)
    except Exception as e:
        print(f"获取HTML内容失败: {e}")
        return []
    
    # 提取JSON数据
    json_data = extract_json_from_script(html_content)
    if json_data:
        print("\n提取的JSON数据:")
        for data in json_data:
            print(data)
            print("-" * 80)
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # If you want to save the prettified version, do it without reassigning soup
    pretty_html = soup.prettify()
    with open('soup2.html', 'w', encoding='utf-8') as file:
        file.write(pretty_html)
    
    # 找到SKU区域
    sku_div = soup.find('div', attrs={'spm-c': 'sku'})
    if not sku_div:
        print("未找到SKU数据区域")
        return []
    
    # 找到所有颜色选项
    color_items = sku_div.find_all('div', class_='skuImageType_imageTypeItem__mL7fq')
    
    # 提取每个颜色选项的数据
    sku_data = []
    for item in color_items:
        sku_info = {
            'color': item.get('spm-index', ''),
            'attr_id': item.get('data-attrid', ''),
            'attr_val_id': item.get('data-attrvalid', ''),
            'is_active': 'skuImageType_active__CFiEd' in item.get('class', []),
            'image_url': item.find('img')['src'] if item.find('img') else ''
        }
        sku_data.append(sku_info)
    
    return sku_data

def main():
    source = 'https://www.dhgate.com/product/a6s-bluetooth-headset-macaron-bluetooth-5/1016743104.html'
    
    # 提取SKU数据
    sku_data = extract_sku_data(source)
    
    if sku_data:
        print("\nSKU数据:")
        for sku in sku_data:
            print(f"\n颜色: {sku['color']}")
            print(f"属性ID: {sku['attr_id']}")
            print(f"属性值ID: {sku['attr_val_id']}")
            print(f"是否选中: {sku['is_active']}")
            print(f"图片URL: {sku['image_url']}")
        print(f"\n总共找到 {len(sku_data)} 个SKU选项")
    else:
        print("未找到SKU数据")

if __name__ == "__main__":
    main()