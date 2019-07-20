import requests
import re
import time
import json
import multiprocessing
from handle_insert_data import lagou_mysql


# 导入request模块
# 城市列表url：  https://www.lagou.com/jobs/allCity.html

class HandleLaGou(object):  # 创建一个拉勾类
    def __init__(self):  # 先创建init方法，在这个方法里面需要有两个方面一个是session，另一个是头部信息
        # 为什么使用session，主要是使用保存cookies信息
        self.lagou_session = requests.session()
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }        
        # 我们还需要定义一个变量，city_list,他就会保存我们所有城市的名称
        self.city_list = ""

    # 获取全国所有城市列表的方法
    def handle_city(self):
        # 可以通过xpath去获取城市列表名称，这里是使用正则表达式来获取
        # 正则表达是方法：复制html源码，查找出一个城市位置，例如廊坊，需要得到的结果是zhaopin/">廊坊</a>
        # city_search = re.compile(r'zhaopin/">(.*?)</a>')
        city_search = re.compile(r'www\.lagou\.com\/.*\/">(.*?)</a>')
        city_url = 'https://www.lagou.com/jobs/allCity.html'
        city_result = self.handle_request(method="GET",url=city_url)
        # print(city_result)
        #使用正则表达式获取城市列表
        self.city_list = city_search.findall(city_result)
        self.lagou_session.cookies.clear()

    def handle_city_job(self,city):
        #现在来发送第一个请求，也就是cookies的第一个get请求，这里需要吧city信息替换掉，也就是改成了%s那部分
        first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput="%city
        #接下来请求它
        first_response = self.handle_request(method='GET',url=first_request_url)
        #接下来就是匹配页数,因为源码中，页面数据主要是class="span\stotalNum">数字多少页</span>，所有匹配它就能匹配到他全部页数了
        total_page_search = re.compile(r'class="span\stotalNum">(\d+)</span>')
        #这样就可以通过正则表达式来进行匹配，，通过search方法来获取，使用group(1)来获取页码
        # total_page = total_page_search.search(first_response).group(1)
        #问题来了，如果这个城市没有岗位信息的话就会出现报错，所有需要try一下
        try:
            total_page = total_page_search.search(first_response).group(1)
            print(city,total_page)
        #如果没有就返回return
        except:
            return
        #如果有好多页的话，那就使用for循环来构造这个页码
        else:
            for i in range(1,int(total_page)+1):
                #那么构造页码要构造到哪里去呢，构造到data里面去
                data = {
                    'pn':i,
                    'kd':'python'
                }
                #这时候就可以来够着post请求了，因为这些用到了post请求，所以在下面的handle_request需要添加一个post
                page_url = "https://www.lagou.com/jobs/positionAjax.json?city=%s&needAddtionalResult=false"%city 
                #没有referer_url这一步的话那就很容易让网站发现你是爬虫，所以需要添加这一步               
                referer_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput="%city                
                #referer的URL需要进行encode
                self.header['Referer'] = referer_url.encode()
                response = self.handle_request(method='POST',url=page_url,data=data,info=city)
                lagou_data = json.loads(response)
                job_list = lagou_data['content']['positionResult']['result']
                for job in job_list:
                    lagou_mysql.insert_item(job)
    
    # 接下来就去请求url，所以需要定义一个请求方法，这个方法需要传入method,url,data,info（参数信息）
    def handle_request(self, method, url, data=None, info=None):
        while True:
            #加入阿布云的动态代理
            proxyinfo = "http://%s:%s@%s:%s" % ('H5HIQ01ZD74SIF3C', 'DE665AC70762940B', 'http-cla.abuyun.com', '9030')
            proxy = {
                "http":proxyinfo,
                "https":proxyinfo
            }
            try:
                if method == 'GET':  # 如果说method等于get，那么就认为他是get请求
                #因为这里加入了阿布云道理，所以get和post请求都需要加上proxies=proxy,timeout=6
                    response = self.lagou_session.get(url=url, headers=self.header,proxies=proxy,timeout=6)
            # 那么它就等于self的lagou_session.get，url等于他的url，header等于self的header，这样就可以获得response信息了
                elif method =='POST':# 如果说method等于post，那么就认为他是post请求
                    response = self.lagou_session.post(url=url,headers=self.header,data=data,proxies=proxy,timeout=6)
            except:
                #需要先请求cookies信息
                self.lagou_session.cookies.clear()
                #重新获取cookies信息
                first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput=" % info
                self.handle_request(method="GET", url=first_request_url)
                #为了不让捉取速度太快而被察觉，所以让它先休眠10秒，10秒这个的话是经过多次测试得来的
                time.sleep(10)
                #休息完后，再来重复上面的信息
                continue
            response.encoding='utf-8'#修改格式
            if '频繁' in  response.text:#如果这里出现频繁，我们需要清除cookies里面的信息，然后再去请求我们的cookies信息
                print(response.text)
                #需要先请求cookies信息
                self.lagou_session.cookies.clear()
                #重新获取cookies信息
                first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput=" % info
                self.handle_request(method="GET", url=first_request_url)
                #为了不让捉取速度太快而被察觉，所以让它先休眠10秒，10秒这个的话是经过多次测试得来的
                time.sleep(10)
                #休息完后，再来重复上面的信息
                continue
            return response.text


if __name__ == '__main__':
    lagou = HandleLaGou()
    lagou.handle_city()
    #引用多进程加速捉取
    #创建一个进程池，两个进程，因为我个人的代理每秒只能发送五个请求，为了稳定所以写2
    pool = multiprocessing.Pool(2)
    # print(lagou.city_list)
    for city in lagou.city_list:#这样就能获取到所有的城市，把这些城市传递到lagou.handle_city_job里面来
        #这样就可以吧我们的数据传递到进程池里面去
        pool.apply_async(lagou.handle_city_job,args=(city,))
    pool.close()
    pool.join()
