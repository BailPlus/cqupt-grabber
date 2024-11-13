#cqupt-grabber:libgrab 抢课模块

URL = 'http://xk1.cqupt.edu.cn' # 可改为“xk2”

import requests,time

def get_json_data(type:str,cookie:str):
    url = URL+'/json-data-yxk.php?type='+type
    res = requests.get(url,headers={'Cookie':cookie})
    return res.json()

class Lesson:
    def __init__(self,raw_data:dict):
        self.raw_data = raw_data
        self.term = raw_data.get('xnxq')    # 学年学期
        self.id = raw_data.get('jxb')   # 教学班id，即该Lesson在服务器的id
        self.classid = raw_data.get('kcbh') # 课程编号
        self.class_name = raw_data.get('kcmc')  # 课程名称
        self.score = float(raw_data.get('xf'))  # 学分
        self.max_member_num = int(raw_data.get('rsLimit')) if raw_data.get('rsLimit') else -1   # 人数限制
        self.update_time = raw_data.get('updateTime')   # 更新时间(有什么用？)
        self.teacher_name = raw_data.get('teaName') # 教师姓名
        self.must = raw_data.get('kclb')    # 课程必修性(str类型)
        self.htype = raw_data.get('kchType')    # 课程类别(如“理论”)
        self.memo = raw_data.get('memo')    # (这是什么？)
class Grabber:
    def __init__(self,cookie:str):
        self.cookie = cookie
    def is_available(self)->bool:
        '''查询是否可以抢课'''
        return requests.get(URL+'/yxk.php',headers={'Cookie':self.cookie},allow_redirects=False).status_code == 200
    def wait_to_available(self,sleep_time:int=1):
        '''产生阻塞，直到可以抢课
sleep_time(int):轮询间隔时间
----------
注意：由于cookie过期和未开始抢课是一个效果，所以请确保cookie有效！否则会无限循环！'''
        while not self.is_available():
            time.sleep(sleep_time)
    def get_bj(self)->list:
        res = get_json_data('bj',self.cookie)
        if res['code'] != 0:
            raise RuntimeError(res['info'])
        return [Lesson(i) for i in res['data']]
    def get_zr(self)->dict:
        res = get_json_data('jctsZr',self.cookie)
        if res['code'] != 0:
            raise RuntimeError(res['info'])
        return [Lesson(i) for i in res['data']]
    def get_rw(self)->dict:
        res = get_json_data('jctsRw',self.cookie)
        if res['code'] != 0:
            raise RuntimeError(res['info'])
        return [Lesson(i) for i in res['data']]
    def get_en(self)->dict:
        res = get_json_data('yyxx',self.cookie)
        if res['code'] != 0:
            raise RuntimeError(res['info'])
        return [Lesson(i) for i in res['data']]
    def get_me(self)->dict:
        res = get_json_data('yxk',self.cookie)
        if res['code'] != 0:
            raise RuntimeError(res['info'])
        return [Lesson(i) for i in res['data']]
    def grab(self,lesson:Lesson)->bool:
        '''选课
lesson(Lesson):课程对象
返回值:选课成功性(bool)'''
        url = URL+'/post.php'
        res = requests.post(url,headers={'Cookie':self.cookie},data=lesson.raw_data)
        res_json = res.json()
        if res_json['code'] != 0:
            print(res_json)
            raise RuntimeError(res_json['info'])
    def close(self):
        url = URL+'/logout.php'
        requests.get(url,headers={'Cookie':self.cookie})
    __enter__ = lambda self:self
    __exit__ = lambda self,*args:self.close()
