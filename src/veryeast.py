import requests
import json
import pymongo

class VeryEast(object):
    Headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "X-Requested-With":"XMLHttpRequest",
        "Cookie":r"closePop=true; td_cookie=833740359; _ga=GA1.2.872748135.1523341077; _gid=GA1.2.1973532055.1523341077; ticket=727bbsSsgVZtHLS0ZY1Z1cTENvuVsXZVNTeM1bInjqslt59VLbpIEIBq25tXgSAlPO0a6%2BHnGkmQ7la0Cd8I; username=waterman; user_type=1; current_app=a%3A1%3A%7Bi%3A1%3Bi%3A1%3B%7D; _expire=1523945892; uid=very_2840997; sdktoken=8681f18f929279ea2ce59fb324c30e06; nickName=18621538364@%u5468%u53E3%u65C5%u5982%u5BB6%u9152%u5E97; avatar=; ps_search_viewcontactlist=10; ps_credit_gain=10; closePop=true; ps_resume_resumelist=10; ps_resume_favoritelist=10; ps_search_index=50",
        "Content-Type":"application/x-www-form-urlencoded"
    }
    PreviewUrl="http://vip.veryeast.cn/resume/preview/{0}"
    SearchUrl="http://vip.veryeast.cn/search/index"
    FormData="pager=%s&per=50&advanced=1&job_id=0&is_search=1&keyword=&keyword_type=1&marital=0&language_level=-1&language_type=-1&resume_type=-1&user_id=&gender=0&domicile_location=&current_location=&work_mode=-1&age_end=&age_start=&work_year=0&desired_salary=-1&degree=0&desired_location=&=&arrival_date=-1&update_date=360&desired_job=&id=0"
    MONGODB_CONFIG = {
        'host': '127.0.0.1',
        'port': 27017,
        'db_name': 'veryeast',
        'username': None,
        'password': None
    }

    def __init__(self):
        try:
            self.headers=VeryEast.Headers
            self.searchUrl=VeryEast.SearchUrl
            self.formData=VeryEast.FormData
            self.con=pymongo.MongoClient(VeryEast.MONGODB_CONFIG['host'],VeryEast.MONGODB_CONFIG['port'])
            self.db=self.con[VeryEast.MONGODB_CONFIG['db_name']]
            self.connected = True
            self.previewUrl=VeryEast.PreviewUrl
        except Exception:
            print(traceback.format_exc())
            sys.exit(1)

    def getBaseData(self):
        lastPage=1
        currentPage=0
        while(currentPage<lastPage):
            currentPage=currentPage+1
            response=requests.post(self.searchUrl,headers=self.headers,data=self.formData%currentPage)
            jsonData=json.loads(response.content.decode('utf-8'))
            if(jsonData==None and jsonData['data']!=None):
                return
            lastPage=jsonData['data']['pager']['allPages']
            dataList=jsonData['data']['list']
            print('currentPage:{0},   lastPage:{1}'.format(currentPage,lastPage))

            if(len(dataList)>0):
                for data in dataList:
                    self.db['baseinfo'].insert(data)
        print('download success!!!')
    
    def getPreview(self):
        self.db

        response=requests.get(self.previewUrl.format)
        