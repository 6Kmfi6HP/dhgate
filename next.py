import re


def parse_html_script(html_content):
    # 使用正则表达式匹配所有 self.__next_f.push 的内容
    pattern = r'self\.__next_f\.push\(\[1,"([^"]*?)"\]\)'
    matches = re.findall(pattern, html_content)
    
    # 连接所有匹配的内容并打印调试信息
    print(f"Found {len(matches)} matches")
    combined_content = ''
    for i, match in enumerate(matches):
        # 只处理长度大于10的匹配内容
        if len(match) > 10:
            print(f"Match {i + 1} length: {len(match)}")
            combined_content += match
    
    print(f"Combined content length: {len(combined_content)}")
    # save to file
    with open('combined_content.txt', 'w') as file:
        file.write(combined_content)
    
    try:
        # 解析合并后的JSON字符串
        import json
        json_obj = json.loads(combined_content)
        return [json_obj]
    except Exception as e:
        print(f"Error parsing combined content. Error: {e}")
        # 如果解析失败，打印部分内容以便调试
        print(f"First 200 chars of combined content: {combined_content[:200]}")
        return []

# 提取完整数据的函数
def extract_data(data_array):
    # Convert array to JSON format
    import json
    return json.dumps(data_array, ensure_ascii=False, indent=2)

# 读取HTML文件
with open('soup2.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# 解析数据
data = parse_html_script(html_content)
# 提取数据
result = extract_data(data)
# 打印结果
import pprint
pprint.pprint(result)
# save to file
with open('data.json', 'w') as file:
    file.write(result)