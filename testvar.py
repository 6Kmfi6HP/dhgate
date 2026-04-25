import re
import json
from typing import Dict, List
import requests
from html_downloader import HEADERS

def parse_attributes(json_data: List[Dict]) -> Dict[str, List[Dict[str, str]]]:
    """
    解析商品属性，返回属性名称和对应的值列表（包含图片URL）
    Args:
        json_data: 包含商品属性的JSON数据列表
    Returns:
        Dict[str, List[Dict[str, str]]]: 属性名称作为key，
            值为包含属性值和图片URL的字典列表
    """
    attributes = {}
    for attr in json_data:
        attr_name = attr['attrName']
        if attr_name == "Shipping from":
            continue
        
        # 提取属性值和对应的图片URL（它们在同一级）
        values = []
        for item in attr['itemAttrvalList']:
            attr_info = {
                'value': item.get('attrValName', ''),
                'image_url': item.get('picUrl', '').replace('200x200', '0x0')
            }
            values.append(attr_info)
        
        attributes[attr_name] = values
    return attributes

def extract_json_data(text: str, pattern: str) -> List[str]:
    """
    从文本中提取JSON数据
    Args:
        text: 要处理的HTML文本内容
        pattern: 用于匹配JSON数据的正则表达式
    Returns:
        List[str]: 去重后的JSON数据列表
    """
    text = text.replace('\\"', '"')
    print(f"开始提取JSON数据，文本长度: {len(text)}")
    print(f"正则表达式: {pattern[:200]}...")
    print(f"开始匹配...")
    matches = re.findall(pattern, text)
    print(f"找到 {len(matches)} 个匹配项")
    return list(set(matches))

def parse_json(json_str: str) -> List[Dict]:
    """解析JSON字符串为Python对象"""
    print(f"开始解析JSON字符串，长度: {len(json_str)}")
    try:
        result = json.loads('[' + json_str + ']')
        print("JSON解析成功")
        return result
    except json.JSONDecodeError as e:
        print(f"解析JSON时出错: {e}")
        print(f"问题JSON字符串: {json_str[:200]}...")  # 只打印前200个字符
        return []

def print_attributes(attributes: Dict[str, List[Dict[str, str]]]) -> None:
    """
    打印属性结果，包括图片URL
    Args:
        attributes: 属性字典，包含属性值和图片URL
    """
    print("\n商品属性解析结果:")
    print("-" * 40)
    for attr_name, values in attributes.items():
        print(f"\n{attr_name}:")
        for i, attr_info in enumerate(values, 1):
            value = attr_info['value']
            image_url = attr_info['image_url']
            print(f"  {i}. {value}")
            if image_url:  # 只有当图片URL存在时才打印
                print(f"     图片: {image_url}")
    print("-" * 40)

def get_html_from_url(url: str) -> str:
    """
    从URL获取HTML内容
    Args:
        url: 目标网页的URL
    Returns:
        str: 网页的HTML内容，如果获取失败则返回空字符串
    """
    print(f"开始获取URL内容: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        content_length = len(response.text)
        print(f"成功获取网页内容，长度: {content_length} 字符")
        return response.text
    except requests.RequestException as e:
        print(f"获取URL内容时出错: {e}")
        return ""

def main():
    """
    主函数：完整的数据获取和处理流程
    1. 从指定URL获取HTML内容
    2. 使用正则表达式提取JSON数据
    3. 解析JSON数据获取商品属性
    4. 打印解析结果
    """
    pattern = r'"itemAttrList":\[(.*?)\](?=,"firstItemAttrList")'
    
    url = "https://www.dhgate.com/product/designer-shoes-sneakers-trainers-men-womens/995849295.html"
    text = get_html_from_url(url)
    
    if not text:
        print("无法获取网页内容")
        return
    
    unique_matches = extract_json_data(text, pattern)
    
    for match in unique_matches:
        json_obj = parse_json(match)
        if json_obj:
            attributes = parse_attributes(json_obj)
            print_attributes(attributes)

if __name__ == "__main__":
    main()