import requests
from lxml import etree
import re
#import execjs

def seedRequest(url,header):
    response = requests.get(url=url,headers=header)
    response.encoding = "utf8"
    return response.text

def func(obj):
    span = obj.group(0)
    num = re.findall('context_kw(\d{1,2})', span, re.I)[0]
    try:
        replace = words[int(num)]
        return replace
    except KeyError:
        print("未找到编号%s的汉字"%num)
        return "#"
    
def htmlReplace(html):
    responseReplace = re.sub('<span class="context_kw\d*?"></span>', func, html)
    return responseReplace

# def get_words_js():
#     with open("./getWords.js","r",encoding="utf8") as fp:
#         js = fp.read()
#     ctx = execjs.compile(js)
#     return ctx.call('parseWord')

def getContentHtml(html):
    tree = etree.HTML(html)
    title = tree.xpath("//div[@class='lf']/h1/text()")[0]
    text = tree.xpath("///div[@class='rdtext']/p/text()")
    concatText = "".join(text)
    print(title)
    print(concatText)
    
if __name__ == '__main__':
    header = {
        "authority": "g.hongshu.com",
        "method": "GET",
        "path": "/content/93416/13877912.html",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "cookie": "pgv_pvi=7004054528; bookfav=%7B%22b93416%22%3A0%7D; pgv_si=s2563727360; Hm_lvt_e966b218bafd5e76f0872a21b1474006=1566288274,1566295321,1566460817; Hm_lpvt_e966b218bafd5e76f0872a21b1474006=1566460817; yqksid=u5j08hk2dgmrtj0hirfv0niss2",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    }
    url = "https://g.hongshu.com/content/93416/13877912.html"
    words = ["，","的","。","刘","人","一","他","是","不","在","有","了","着","”","“","秀","大","上","道","歆","个","名","下","地"]
    
    html = seedRequest(url,header)
    getContentHtml(htmlReplace(html))