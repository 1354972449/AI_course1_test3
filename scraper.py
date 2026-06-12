import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

base_url = 'https://ggzyjy.xuancheng.gov.cn/xcspfront/zfcg/trade_info.html'

# 运营商相关关键词
operator_keywords = [
    '通信', '网络', '宽带', '光纤', '5G', '4G', '基站', '机房', '信息化',
    '智能化', '监控', '安防', '系统集成', '软件', '数据', '云', '服务器',
    '交换机', '路由器', '专线', '物联网', '智慧', '数字', '电子', '电脑',
    '办公设备', '打印机', '复印机', '多媒体', '教学设备', 'LED', '显示屏',
    '广播', '音响', '视频', '会议', '录播', '精品课', '校园网', '局域网'
]

def is_operator_related(title):
    """判断项目是否与运营商相关"""
    title_lower = title.lower()
    for keyword in operator_keywords:
        if keyword in title:
            return True
    return False

def scrape_page(page_num=1, info_type='', time_range=''):
    """抓取指定页面数据"""
    params = {
        'pageNo': page_num,
        'pageSize': 15,
    }
    
    if info_type:
        params['infoType'] = info_type
    if time_range:
        params['timeRange'] = time_range
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}")
        return None

def parse_list_page(html):
    """解析列表页面"""
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    
    # 查找项目列表 - 根据网站结构选择
    table = soup.find('table')
    if table:
        rows = table.find_all('tr')[1:]  # 跳过表头
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                title = cols[0].get_text(strip=True)
                date = cols[1].get_text(strip=True)
                link = cols[0].find('a')
                url = link.get('href') if link else ''
                
                items.append({
                    'title': title,
                    'date': date,
                    'url': url
                })
    
    # 备选：查找div列表
    if not items:
        item_divs = soup.find_all('div', class_='list-item')
        for div in item_divs:
            title_elem = div.find('a')
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                date_elem = div.find('span', class_='date')
                date = date_elem.get_text(strip=True) if date_elem else ''
                
                items.append({
                    'title': title,
                    'date': date,
                    'url': url
                })
    
    return items

def main():
    """主函数"""
    print("开始抓取宣城公共资源交易平台数据...")
    
    all_items = []
    
    # 抓取采购意向公开数据（近一个月）
    print("\n抓取采购意向公开数据...")
    for page in range(1, 12):  # 11页
        print(f"  正在抓取第 {page} 页...")
        html = scrape_page(page, info_type='017001001', time_range='month')
        if html:
            items = parse_list_page(html)
            all_items.extend(items)
            print(f"    获取 {len(items)} 条记录")
    
    # 抓取中标(成交)公告数据（近一个月）
    print("\n抓取中标(成交)公告数据...")
    for page in range(1, 9):  # 8页
        print(f"  正在抓取第 {page} 页...")
        html = scrape_page(page, info_type='017001006', time_range='month')
        if html:
            items = parse_list_page(html)
            all_items.extend(items)
            print(f"    获取 {len(items)} 条记录")
    
    # 抓取招标公告数据（近一个月）
    print("\n抓取招标公告数据...")
    for page in range(1, 21):  # 20页
        print(f"  正在抓取第 {page} 页...")
        html = scrape_page(page, info_type='017001002', time_range='month')
        if html:
            items = parse_list_page(html)
            all_items.extend(items)
            print(f"    获取 {len(items)} 条记录")
    
    # 筛选运营商相关项目
    print("\n筛选运营商相关项目...")
    operator_items = [item for item in all_items if is_operator_related(item['title'])]
    
    print(f"总共获取 {len(all_items)} 条记录")
    print(f"其中运营商相关项目 {len(operator_items)} 条")
    
    # 输出结果
    print("\n运营商相关项目列表:")
    for i, item in enumerate(operator_items[:20], 1):
        print(f"{i}. [{item['date']}] {item['title']}")
    
    return operator_items

if __name__ == '__main__':
    main()