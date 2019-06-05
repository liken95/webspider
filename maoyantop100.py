from requests.exceptions import RequestException
import requests
from bs4 import BeautifulSoup
import json
import time

def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        return None

# 1 用正则提取内容
def parse_one_page1(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    # re.S 表示匹配任意字符。如果不加，无法匹配换行符。

    items = re.findall(pattern,html)
   #print(items)
    for item in items:
        yield {
            'index':item[0],
            'image':item[1],
            'title':item[2],
            'actor':item[3].strip()[3:],
            'time':item[4].strip()[5:],
            'score':item[5]+item[6]

        }

# 2 用beautifulsoup + find_all 提取
def parse_one_page2(html):
    soup = BeautifulSoup(html,'lxml')
    items = range(10)
    for item in items:
        yield {
        'index': soup.find_all(name='i',class_='board-index')[item].string,
        'image': soup.find_all(class_='board-img')[item].attrs['data-src'],
            # board-ima的img节点，注意浏览器element里面的是src节点，而network里面的是data-src节点，要用这个才能正确返回。
        'name': soup.find_all(name='p',class_='name')[item].string.strip(),
        'star': soup.find_all(name='p',class_='star')[item].string.strip()[3:],
        'time' : soup.find_all(name='p',class_='releasetime')[item].string[5:],
        'score' : soup.find_all(class_='integer')[item].string.strip() + \
               soup.find_all(class_='fraction')[item].string.strip()
        }

# 3 用beautiful + css 提取
def parse_one_page(html):
    soup = BeautifulSoup(html,'lxml')
    items = range(10)
    for item in items:
        yield {
        'index': soup.select('.board-index')[item].string,
        'image': soup.select('.board-img')[item].attrs['data-src'],
            # board-ima的img节点，注意浏览器element里面的是src节点，而network里面的是data-src节点，要用这个才能正确返回。
        'name': soup.select('.name')[item].string.strip(),
        'star': soup.select('.star')[item].string.strip()[3:],
        'time' : soup.select('.releasetime')[item].string[5:],
        'score' : soup.select('.integer')[item].string.strip() + \
               soup.select('.fraction')[item].string.strip()
        }

def write_to_file(content):
    with open('result.txt','a',encoding='utf-8') as f:
        f.write(json.dumps(content,ensure_ascii=False) + '\n')

def main(offset):
    url = 'http://maoyan.com/board/4?offset='+str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)

if __name__ == "__main__":
    for i in range(10):
        main(offset=i*10)
    time.sleep(1)