# 红薯中文网小说爬取

#### 描述
红薯中文小说网，采用了js动态加载小说内容部分汉字或符号。本仓库介绍如何破解js将小说内容完整的爬取下来。

我们首先用浏览器F12查看下页面情况，页面连接：https://g.hongshu.com/content/93416/13877912.html
<img src="./002.png">
图片中少量汉字都是使用```span```标签对应上去的，我们在点击span标签的时候在右边可以看到
```css
.context_kw23::before {
    content: "地";
}
```
很显然，这些内容是通过js动态加载上去的。我们仔细观察所有span标签，看他的类属性都是以```context_kw```开头，后面再加上数字编号。我们可以大胆猜测每一个数字编号对应一个汉字或符号。然后我们再研究js。与我们相关的js就在响应的html中。<a href="./getWords.js">js</a>
研究发现编码对应的汉字或符号在```words```变量中，索引与数字编号对应。
<img src="./001.png">
上图是调试js的截图
- data是加密过的内容，keywords是解码的密码，通过js中的解密函数生成了编码的列表secWords，然后通过```fromCharCode```函数生成对应的汉字列表words

js代码写的很复杂，其实大可不必研究其生成过程（先研究的可以从words生成地方往回推），可以将js代码复制到本地进行运行，生成我们所需要的words列表即可。  
附上全部代码：
```python
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
```
> 上面代码注释掉的函数是python运行本地js的函数，有兴趣的可以研究下。我的因为js文件中有语法问题运行失败了（在浏览器运行没问题）

## 2019-8-24更新
**经多次测试发现，每个页面的words都不一样，手动获取words列表不适合大规模爬取。如果使用seleumns的话效率又跟不上，所以我又研究了下如何在本地运行js代码。**
首先，我们要将响应页面中的js内容分离出来，并做一定的修改：
```python
def createJs(response):   #将响应内容的js内容写入文件，并删除修改部分内容
    jsText = re.findall('<script type="text/javascript">.*?(var CryptoJS.*?)</script>',response,flags=re.S)[0]
    jsText = re.sub('(for\(var i=0x0;i<words.*?document.*?\}\})',"",jsText,flags=re.S)
    jsText = re.sub('var n=document.*?\(n\);\}',"",jsText,flags=re.S)
    jsText = re.sub('if\(top\[.*?\];\}', "", jsText, flags=re.S)
    jsText = re.sub('typeof document', "'object'", jsText, flags=re.S)
    # with open("./createJs.js","w",encoding="utf8") as fm:
    #     fm.write("function parseWord(){" + jsText + "return words;}")
    return "function parseWord(){" + jsText + "return words;}"
```
> js内容中含有document、window对象，这些对象的调用必须浏览器中才能运行。所以要想在本地运行，这些内容必须删除或替换掉。上面代码中就做了此处理。具体做了哪些修改可参考GitHub中```example.js```文件。
接下来便可以本地运行js文件了
```python
def get_words_js(js):   #运行js代码，返回words列表
    # with open("./createJs.js","r",encoding="utf8") as fp:
    #     js = fp.read()
    data = js2py.eval_js(js)
    return data()
```
GitHub仓库中有```testJs.py```文件,运行如下。
<img src="./006.png">
获取到words列表就可以按照之前发布的内容的进行爬取了。
#### 附上修改后的完整代码
```python
import requests
from lxml import etree
import re
import js2py    # 运行js的库

def seedRequest(url,header):  #发送请求，返回响应内容
    response = requests.get(url=url,headers=header)
    response.encoding = "utf8"
    print(response.status_code)
    return response.text

def createJs(response):   #将响应内容的js内容写入文件，并删除修改部分内容
    jsText = re.findall('<script type="text/javascript">.*?(var CryptoJS.*?)</script>',response,flags=re.S)[0]
    jsText = re.sub('(for\(var i=0x0;i<words.*?document.*?\}\})',"",jsText,flags=re.S)
    jsText = re.sub('var n=document.*?\(n\);\}',"",jsText,flags=re.S)
    jsText = re.sub('if\(top\[.*?\];\}', "", jsText, flags=re.S)
    jsText = re.sub('typeof document', "'object'", jsText, flags=re.S)
    # with open("./createJs.js","w",encoding="utf8") as fm:
    #     fm.write("function parseWord(){" + jsText + "return words;}")
    return "function parseWord(){" + jsText + "return words;}"
    
def get_words_js(js):   #运行js代码，返回words列表
    # with open("./createJs.js","r",encoding="utf8") as fp:
    #     js = fp.read()
    data = js2py.eval_js(js)
    return data()

def func(obj):      #re.sub中调用的函数，将匹配的内容进行处理，并返回相对应的汉字
    span = obj.group(0)
    num = re.findall('context_kw(\d{1,2})', span, re.I)[0]
    try:
        replace = words[int(num)]
        return replace
    except KeyError:
        print("未找到编号%s的汉字" % num)
        return "#"

def htmlReplace(html):    #正则匹配到span标签并替换成对应汉字
    responseReplace = re.sub('<span class="context_kw\d*?"></span>', func, html)
    return responseReplace

def getContentHtml(response):   #解析页面，获取小说内容
    tree = etree.HTML(response)
    title = tree.xpath("//div[@class='lf']/h1/text()")[0]
    text = tree.xpath("///div[@class='rdtext']/p/text()")
    concatText = "".join(text) 
    print(title)  
    print(text)
    
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
    url = "https://g.hongshu.com/content/93416/13901181.html"
    # words = ["，","的","。","刘","人","一","他","是","不","在","有","了","着","”","“","秀","大","上","道","歆","个","名","下","地"]
    
    html = seedRequest(url,header)
    words = get_words_js(createJs(html))
    getContentHtml(htmlReplace(html))
```
运行结果截图：
<img src="./005.png">

#### 本人原创，请多多指正
#### 联系我：768348710@qq.com