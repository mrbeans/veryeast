import requests
import json
import pymongo
from lxml import etree

class VeryEast(object):
    Headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "X-Requested-With":"XMLHttpRequest",
        "Cookie":r"_ga=GA1.2.872748135.1523341077; ps_search_viewcontactlist=10; ps_credit_gain=10; ps_resume_resumelist=10; ps_resume_favoritelist=10; ps_search_index=50; UM_distinctid=162b976c14924d-03297a56208689-3a614f0b-1fa400-162b976c14a231; td_cookie=944934255; _gid=GA1.2.22497359.1524715056; Hm_lvt_bb6401d33941b99b0b91e2622ae7596d=1524043515,1524109454,1524452968,1524715056; ticket=b82eeG4otXky%2FOfojvpN4Ya1Fjk%2FDpzlVUljGOSYhEEUIyGB9LT%2FqX1%2FdIuyl3Rj5JhG%2B0aY2xnp1jrT%2BuxE; username=waterman; user_type=1; current_app=a%3A1%3A%7Bi%3A1%3Bi%3A1%3B%7D; _expire=1525319936; closePop=true; uid=very_2840997; sdktoken=8681f18f929279ea2ce59fb324c30e06; nickName=18621538364@%u5468%u53E3%u65C5%u5982%u5BB6%u9152%u5E97; avatar=; Hm_lpvt_bb6401d33941b99b0b91e2622ae7596d=1524715076",
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
        cursor=self.db['baseinfo'].find({"gender": " 男","work_year": "4","degree": "高中 ","desire_job_num": 2},{"user_id": 1}).limit(1)
        try:
            for data in cursor:
                #response=requests.get(self.previewUrl.format(data["user_id"]),headers=self.headers)
                response=requests.get('http://vip.veryeast.cn/resume/preview/814048',headers=self.headers)
                response.encoding='utf-8'
                tree=etree.HTML(response.content)
                preview={}
                preview['last_view_time']=tree.xpath('//*[@id="preview"]/div[@class="c_last_time"]/span/strong/text()')[0]
                preview['last_update_time']=tree.xpath('//*[@id="preview"]/div[@class="c_update_time"]/strong/text()')[0]

                resume_preview=tree.xpath('//*[@id="preview"]/div[@class="resume_preview"]')[0]
                
                resume_preview_top=resume_preview.xpath('div[@class="resume_preview_top"]')[0]
                
                resume_preview_top_right=resume_preview_top.xpath('div[@class="resume_preview_top_right"]')[0]
                
                userface=resume_preview_top_right.xpath('a/img/@src')
                if(len(userface)>0):
                    preview['userface']=userface[0]
                
                #左侧基本信息
                resume_preview_top_left=resume_preview_top.xpath('div[@class="resume_preview_top_left"]')[0]
                
                resume_preview_top_left_list=resume_preview_top_left.xpath('div[@class="preview_left_list"]')
                baseinfo={}
                for info in resume_preview_top_left:
                    addr=info.xpath('ul[contains(@class,"addr")]')
                    if(addr==None or len(addr)<=0):
                        continue
                    lis=addr[0].xpath('li/text()')
                    for li in lis:
                        key,value=li.replace(' ','').replace('：',':').split(':')
                        if(key=='现居地'):
                            baseinfo['living_place']=value
                        elif(key=='户籍地'):
                            baseinfo['domicile_place']=value
                        elif(key=='国籍'):
                            baseinfo['country']=value
                        elif(key=='政治面貌'):
                            baseinfo['political_status']=value
                        elif(key=='民族'):
                            baseinfo['nation']=value
                        elif(key=='证件号码'):
                            baseinfo['IDCard']=value
                preview['baseinfo']=baseinfo
                #下面的详细内容
                preview_main_list=resume_preview.xpath('div[@class="resume_preview_main"]')
                for main in preview_main_list:
                    title=main.xpath('h1/text()')[0]
                    if(title=='最近一份工作'):
                        lastest_work={}
                        company=main.xpath('ul/li/strong/text()')[0].strip().split(' ')
                        lastest_work['company_name']=company[0]
                        del company[0]
                        lastest_work['company_date']="".join(company)
                        
                        company_detail=main.xpath('ul/li[not(0)]/text()')
                        for detail in company_detail:
                            if(len(detail.strip())<=0):
                                continue
                            k,v=detail.replace(' ','').replace('：',':').split(':')
                            if(k=='企业性质'):
                                lastest_work['nature']=v
                            elif(k=='职位'):
                                lastest_work['job_title']=v
                            else:
                                raise Exception('最近一份工作-有未处理的字段，地址：%s'%self.previewUrl.format(data["user_id"]))
                        print(lastest_work)
                    elif(title=='求职意向'):
                        job_intension={}
                    elif(title=='工作经验'):
                        pass
                    elif(title=='技能与特长'):
                        pass
                    elif(title=='教育经历'):
                        pass
        finally:
            cursor.close()