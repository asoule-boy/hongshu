import js2py

with open("./createJs.js","r",encoding="utf8") as fp:
    js = fp.read()
    
data = js2py.eval_js(js)


print(data())