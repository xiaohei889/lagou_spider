from sqlalchemy import create_engine,Integer,String,Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column

#创建数据库连接，这里使用的是mysql和pymysql驱动，然后加上数据库的用户名和密码,端口号，数据库名和格式utf8
engine = create_engine('mysql+pymysql://root:root@47.98.112.166:3306/lagou?charset=utf8')
#操作数据库。需要我们创建一个session,这里需要我们传入一个参数bind，它绑定上门创建好的连接engine，这样session就创建好了
Session = sessionmaker(bind=engine)

#声明一个基类
Base = declarative_base()

class Lagoutables(Base):
    #表名称
    __tablename__ = 'lagou_data'
    #id,它需要指定他的类型，integer类型，设置primary_key它是一个主键，而且autoincrement自动增长
    id = Column(Integer,primary_key=True,autoincrement=True)
    #岗位id,指定类型和设置非空字段
    positionID = Column(Integer,nullable=True)
    # 经度
    longitude = Column(Float, nullable=False)
    # 纬度
    latitude = Column(Float, nullable=False)
    # 岗位名称
    positionName = Column(String(length=50), nullable=False)
    # 工作年限
    workYear = Column(String(length=20), nullable=False)
    # 学历
    education = Column(String(length=20), nullable=False)
    # 岗位性质
    jobNature = Column(String(length=20), nullable=True)
    # 公司类型
    financeStage = Column(String(length=30), nullable=True)
    # 公司规模
    companySize = Column(String(length=30), nullable=True)
    # 业务方向
    industryField = Column(String(length=30), nullable=True)
    # 所在城市
    city = Column(String(length=10), nullable=False)
    # 岗位标签
    positionAdvantage = Column(String(length=200), nullable=True)
    # 公司简称
    companyShortName = Column(String(length=50), nullable=True)
    # 公司全称
    companyFullName = Column(String(length=200), nullable=True)
    # 公司所在区
    district = Column(String(length=20), nullable=True)
    # 公司福利标签
    companyLabelList = Column(String(length=200), nullable=True)
    # 工资
    salary = Column(String(length=20), nullable=False)
    # 抓取日期
    crawl_date = Column(String(length=20), nullable=False)

if __name__ == '__main__':
    #创建数据表
    Lagoutables.metadata.create_all(engine)