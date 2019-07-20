#首先需要导入数据和session连接
from create_lagou_tables import Lagoutables
from create_lagou_tables import Session
import time

class HandleLagouData(object):
    def __init__(self):
        #首先实例化这个session信息
        self.mysql_session = Session()

    #定义数据的存储方法
    def insert_item(self,item):
        #当前捉取的日期，也就是今天，通过time.strftime进行格式化
        date = time.strftime("%Y-%m-%d",time.localtime())
        data = Lagoutables(
            #岗位ID
            positionID = item['positionId'],
            # 经度
            longitude=item['longitude'],
            # 纬度
            latitude=item['latitude'],
            # 岗位名称
            positionName=item['positionName'],
            # 工作年限
            workYear=item['workYear'],
            # 学历
            education=item['education'],
            # 岗位性质
            jobNature=item['jobNature'],
            # 公司类型
            financeStage=item['financeStage'],
            # 公司规模
            companySize=item['companySize'],
            # 业务方向
            industryField=item['industryField'],
            # 所在城市
            city=item['city'],
            # 岗位标签
            positionAdvantage=item['positionAdvantage'],
            # 公司简称
            companyShortName=item['companyShortName'],
            # 公司全称
            companyFullName=item['companyFullName'],
            # 公司所在区
            district=item['district'],
            # 公司福利标签，通过逗号 join来进行拼接
            companyLabelList=','.join(item['companyLabelList']),
            salary=item['salary'],
            # 抓取日期
            crawl_date=date
        )

        #在存储之前先查一下当前的表有没有这条数据,通过self.mysql_session.query来查询，查询Lagoutables的，       
        #通过.filter老过滤，过滤Lagoutables.crawl_date，也就是说通过每一天来去重，每一天不能有相同的岗位数据
        query_result = self.mysql_session.query(Lagoutables).filter(Lagoutables.crawl_date==date,
                                                                    Lagoutables.positionID==item['positionId']).first()
        
        if query_result:
            #如果数据已存在那就显示岗位信息已存在，然后打印岗位新的id城市和名字
            print('该岗位信息已存在%s:%s:%s'%(item['positionId'],item['city'],item['positionName']))

        else:
            #插入数据
            self.mysql_session.add(data)
            #提交数据到数据库
            self.mysql_session.commit()
            print('新增岗位信息%s'%item['positionId'])

#接下来就是创建这个类的实例，然后在爬虫文件中引用这个方法就行了
lagou_mysql = HandleLagouData()