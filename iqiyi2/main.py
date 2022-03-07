# -*- coding: utf-8 -*-
import json
from ntpath import join
import os
import re
import time
import requests
import random
import string
import hashlib
import time
import re
from urllib.parse import unquote

import requests

from dailycheckin import CheckIn


class IQIYI2(CheckIn):
    name = "爱奇艺2"

    def __init__(self, check_item):
        self.check_item = check_item

    @staticmethod
    def parse_cookie(cookie):
        p00001 = re.findall(r"P00001=(.*?);", cookie)[0] if re.findall(r"P00001=(.*?);", cookie) else ""
        p00002 = re.findall(r"P00002=(.*?);", cookie)[0] if re.findall(r"P00002=(.*?);", cookie) else ""
        p00003 = re.findall(r"P00003=(.*?);", cookie)[0] if re.findall(r"P00003=(.*?);", cookie) else ""
        dfp = re.findall(r"dfp=(.*?);", cookie)[0] if re.findall(r"dfp=(.*?);", cookie) else ""
        return p00001, p00002, p00003, dfp

    def main(self):
        p00001, p00002, p00003, dfp = self.parse_cookie(self.check_item.get("cookie"))
        user = {
          'P00001': p00001,
          'P00003': p00003,
          'dfp': dfp
        }
        log = []
        startime = time.time()
        vipInfo = info(user)
        vipInfo.update()
        log.append(vipInfo.go_checkin())                    #签到
        log.append(dailyTasks(user).main())                 #日常任务
        if vipInfo.type:
            log.append(vipTasks(user).main())               #会员任务
        # log.append(shake(user,shareUserIds).main())         #摇一摇
        log.append(vip_activity(user).main())               #会员礼遇日
        #log.append(spring_activity(user,uniqueCodes).main())#春节抽奖
        log.insert(0,vipInfo.main())                        #获取情况
        duration = round(time.time() - startime, 3)
        log.append(f"共耗时{duration}秒")

        msg = [
          {
            "name": "日志",
            "value": ''.join(log)
          }
        ]
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


class init(object):#初始化父类

    def __init__(self,user):
        self.P00001 = user.get('P00001')
        self.P00003 = user.get('P00003')
        self.dfp = user.get('dfp')
        self.qyid = self.md5(self.strRandom(16))
        self.pushtitle = '' #微信推送标题
        self.logbuf = ['']

    def strRandom(self,num):#num长度随机字符串 a-z A-Z 0-9
        return ''.join(random.sample(string.ascii_letters + string.digits, num))

    def md5(self,data):#md5加密
        return hashlib.md5(bytes(data, encoding='utf-8')).hexdigest()

    def splice(self,t,e=None):#拼接 连接符 数据 特殊符号（可不填）
        buf = []
        for key,value in t.items():
            buf.append('='.join([key,str(value)]))
        if e != None:
            buf.append(e)
            return(self.md5('|'.join(buf)))
        return('&'.join(buf))

    def message_id(self):#消息代码生成
        t = round(time.time()*1000)
        buf = []
        for zm in'xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx':
            n = int((t + random.random()*16)%16)
            t = int(t/16)
            if zm == 'x':
                buf.append(hex(n)[2])
            elif zm == 'y':
                buf.append(hex(7&n|8)[2])
            else:
                buf.append(zm)
        return ''.join(buf)

class info(init):#身份信息
    def __init__(self,user):
        init.__init__(self, user)

        #natural_month_sign_status
        self.todaySign = False      #签到标志
        self.cumulateSignDays = ''  #连签天数
        self.brokenSignDays = ''    #断签天数

        #info_action
        self.phone = ''             #绑定手机

        #growth_aggregation()
        self.viewTime = ''          #观看时长
        self.todayGrowthValue = ''  #今日成长
        self.distance = ''          #升级还需
        self.level = ''             #会员等级
        self.deadline_date = ''     #VIP到期时间
        self.growthvalue = ''       #当前成长
        self.nickname = '未登录'    #昵称
        self.vipType = 0            #会员类型
        self.paidSign = ''          #付费标志
        self.type = False           #是否是会员


        self.distance_value = 0
        self.todayGrowthValue_value = 0

    def info_action(self): #身份信息
        data = {'agenttype':'11','authcookie':self.P00001,'dfp':'','fields':'userinfo,private','ptid':'03020031010000000000','timestamp':round(time.time()*1000)}
        data['qd_sc'] = self.md5(self.splice(data)+'w0JD89dhtS7BdPLU2')
        url = f"https://passport.iqiyi.com/apis/profile/info.action?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                self.phone = f"\n账户信息：{res['data']['userinfo']['phone']}"
            else:
                self.logbuf.append(f"获取信息失败：{res['msg']}")
        except requests.RequestException as e:
            self.logbuf.append(f"获取信息失败：{e}")

    def natural_month_sign_status(self):
        data = {'appKey':'lequ_rn','authCookie':self.P00001,'task_code':'natural_month_sign_status','timestamp':round(time.time()*1000)}
        data['sign'] = self.splice(data,'cRcFakm9KSPSjFEufg3W')
        header = {"Content-type": "application/json"}
        post_data = {"natural_month_sign_status":{"verticalCode":"iQIYI","taskCode":"iQIYI_mofhr","authCookie":self.P00001,"qyid":self.qyid,"agentType":"11","agentVersion":"11.3.5"}}
        url = f"https://community.iqiyi.com/openApi/task/execute?{self.splice(data)}"
        try:
            res = requests.post(url,headers=header,data=json.dumps(post_data))
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                if res['data']['code'] == 'A0000':
                    self.todaySign = res['data']['data']['todaySign']
                    self.cumulateSignDays = f"{res['data']['data']['cumulateSignDays']}天"
                    if res['data']['data']['brokenSignDays'] != 0:
                        self.brokenSignDays = f"，断签{res['data']['data']['brokenSignDays']}天"
                    else:
                        self.brokenSignDays = ''
                else:
                    self.logbuf.append(f"自然月情况获取失败：{res['data']['msg']}")
            else:
                self.logbuf.append(f"自然月情况获取失败：{res['message']}")
        except requests.RequestException as e:
            self.logbuf.append(f"自然月情况获取失败：{e}")

    def month(self):#月累计获得奖励
        data = {'appname':'rewardDetails','qyid':self.qyid,'messageId':'rewardDetails_'+self.message_id(),'P00001':self.P00001,'lang':'zh_cn','pageNum':1,'pageSize':200}
        url = f"https://tc.vip.iqiyi.com/taskCenter/reward/queryDetail?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                reward_growth = reward_integral = reward_vip = 0
                nowMonth = time.strftime("%Y-%m", time.localtime())
                for reward in res['data'].get('userTaskResults',[]):
                    if nowMonth in reward['createTimeDesc']:
                        taskGiftType = reward['taskGiftType']
                        if taskGiftType == 1:
                            reward_growth += reward['taskGiftValue']
                        elif taskGiftType == 4:
                            reward_integral += reward['taskGiftValue']
                        elif taskGiftType == 2:
                            reward_vip += reward['taskGiftValue']
                    else:
                        break
                if reward_growth + reward_integral + reward_vip > 0:
                    self.logbuf.append('本月任务获得：')
                    if reward_growth != 0:
                        self.logbuf.append(f"-- 成长值 ：{reward_growth}点")
                    if reward_integral != 0:
                        self.logbuf.append(f"-- 积  分 ：{reward_integral}点")
                    if reward_vip != 0:
                        self.logbuf.append(f"-- VIP天数：{reward_vip}天")
            else:
                self.logbuf.append(f"本月奖励查询失败：{res['msg']}")
        except requests.RequestException as e:
            self.logbuf.append(f"本月奖励查询获取失败：{e}")

    def growth_aggregation(self):#成长聚合
        data = {'messageId':self.message_id(),'platform':'97ae2982356f69d8','P00001':self.P00001,'responseNodes':'duration,growth,viewTime','_':round(time.time()*1000),'callback':'Zepto'+str(round(time.time()*1000))}
        url = f"https://tc.vip.iqiyi.com/growthAgency/growth-aggregation?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = json.loads(res.text.split('(')[1].split(')')[0])['data']
            if res:
                if not res.get('code'):
                    if res['user'].get('type') == 1:
                        self.type = True
                    self.nickname = res['user']['nickname']
                    if self.type:
                        self.vipType = res['user']['vipType']
                        self.deadline_date = f"\n到期时间：{res['user']['deadline']}"
                        if res['user']['paidSign'] == 0:
                            self.paidSign = '非付费'
                        else:
                            self.paidSign = ''
                        if self.vipType == 1:
                            self.paidSign += '黄金会员'
                        elif self.vipType == 4:
                            self.paidSign += '星钻会员'
                        else:
                            self.paidSign += '会员'
                        if res['growth']:
                            self.todayGrowthValue = f"\n今日成长：{res['growth']['todayGrowthValue']}点"
                            self.distance = f"\n升级还需：{res['growth']['distance']}点"
                            self.level = f"\n会员等级：LV{res['growth']['level']}"
                            #self.deadline_date = f"\n到期时间：{res['growth']['deadline']}"
                            self.growthvalue = f"\n当前成长：{res['growth']['growthvalue']}点"
                            self.distance_value = res['growth']['distance']
                            self.todayGrowthValue_value = res['growth']['todayGrowthValue']

                    else:
                        self.paidSign = "非会员"
                    if res['viewTime']['time'] != 0:
                        self.viewTime = f"\n今日观看：{int(res['viewTime']['time']/60)}分钟"
                else:
                    self.logbuf.append(f"{res['msg']}")
            else:
                self.logbuf.append('用户信息获取失败：cookie失效')
        except requests.RequestException as e:
            self.logbuf.append(f"用户信息获取失败：{e}")

    def update(self):#更新信息
        self.info_action()
        self.natural_month_sign_status()
        self.growth_aggregation()


    def all_info(self):#统计信息

        self.logbuf.insert(1,f"[ {self.nickname} ]：{self.paidSign}{self.phone}{self.level}{self.todayGrowthValue}{self.growthvalue}{self.distance}{self.deadline_date}{self.viewTime}\n本月签到：{self.cumulateSignDays}{self.brokenSignDays}")

    def checkin(self):#签到
        data = {"agentType":"1","agentversion":"1.0","appKey":"basic_pcw","authCookie":self.P00001,"qyid":self.qyid,"task_code":"natural_month_sign","timestamp":round(time.time()*1000),"typeCode":"point","userId":self.P00003}
        data['sign'] = self.splice(data,"UKobMjDMsDoScuWOfp6F")
        url = f"https://community.iqiyi.com/openApi/task/execute?{self.splice(data)}"
        header = {'Content-Type':'application/json'}
        post_data = {"natural_month_sign":{"agentType":"1","agentversion":"1","authCookie":self.P00001,"qyid":self.qyid,"taskCode":"iQIYI_mofhr","verticalCode":"iQIYI"}}
        try:
            res = requests.post(url,headers=header,data=json.dumps(post_data))
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                if res['data']['code'] == 'A0000':
                    buf =[]
                    for value in res['data']['data']['rewards']:
                        if value['rewardType'] == 1:            #成长值
                            buf.append(f"成长值+{value['rewardCount']}点" )
                        elif value['rewardType'] == 2:          #VIP天数
                            buf.append(f"VIP+{value['rewardCount']}天" )
                        elif value['rewardType'] == 3:          #积分
                            buf.append(f"积分+{value['rewardCount']}点" )
                        elif value['rewardType'] == 4:          #补签卡
                            buf.append(f"补签卡+{value['rewardCount']}张" )
                    return f"签到：{'，'.join(buf)}"
                else:
                    return f"签到失败：{res['data']['msg']}"
            else:
                return f"签到失败：{res['message']}"
        except requests.RequestException as e:
            return f"签到失败：{e}"

    def go_checkin(self):#去签到
        buf = ['']
        if not self.todaySign:
            buf.append(self.checkin())
        else:
            buf.append('签到：已完成')
        return '\n'.join(buf)

    def main(self):
        self.update()
        self.all_info()
        self.month()
        if self.type:
            if self.todayGrowthValue_value != 0:
                self.pushtitle = f"{self.nickname}：今日成长值+{self.todayGrowthValue_value}点,预计{1+int(self.distance_value/self.todayGrowthValue_value)}天后升级"
            else:
                self.pushtitle = f"{self.nickname}：今日成长值+{self.todayGrowthValue_value}点"
        else:
            self.pushtitle = f"{self.nickname}：爱奇艺签到"
        return '\n'.join(self.logbuf)

class vipTasks(init):#会员任务

    def __init__(self,user):
        init.__init__(self, user)
        #会员任务列表及任务状态
        self.tasks = [{'name':'观影保障','taskCode':'Film_guarantee','status':2},{'name':'购买年卡','taskCode':'yearCardBuy','status':2},{'name':'赠片','taskCode':'GIVE_CONTENT','status':2},{'name':'升级权益','taskCode':'aa9ce6f915bea560','status':2},{'name':'并行下载','taskCode':'downloadTogether','status':2},{'name':'预约下载','taskCode':'reserveDownload','status':2},{'name':'音频模式','taskCode':'VipAudioMode','status':2},{'name':'有财频道','taskCode':'VipFinancialChannel','status':2},{'name':'查看报告','taskCode':'checkReport','status':2},{'name':'发送弹幕','taskCode':'vipBarrage','status':2},{'name':'浏览书库','taskCode':'NovelChannel','status':2},{'name':'百度借钱','taskCode':'1231231231','status':2},{'name':'观影30分钟','taskCode':'WatchVideo60mins','status':2},{'name':'浏览福利','taskCode':'b6e688905d4e7184','status':2},{'name':'看热播榜','taskCode':'a7f02e895ccbf416','status':2},{'name':'邀请摇奖','taskCode':'SHAKE_DRAW','status':2},{'name':'活跃观影','taskCode':'8ba31f70013989a8','status':2},{'name':'完善资料','taskCode':'b5f5b684a194566d','status':2},{'name':'自动续费','taskCode':'acf8adbb5870eb29','status':2},{'name':'加盟i联盟','taskCode':'UnionLead','status':2},{'name':'关注i联盟','taskCode':'UnionWechat','status':2},{'name':'权益答题','taskCode':'RightsTest','status':2},{'name':'关注微信','taskCode':'843376c6b3e2bf00','status':2}]

    def query_user_task(self): #获取任务列表及状态 0：待领取 1：已完成 2：未开始 4：进行中
        data = {"P00001":self.P00001,"autoSign":"yes"}
        url = f"https://tc.vip.iqiyi.com/taskCenter/task/queryUserTask?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                self.tasks = []
                for taskgroup in res['data']['tasks']: #in ['daily']: #['actively','daily']: #in res['data']['tasks']:
                    for item in res['data']['tasks'].get(taskgroup,[]):
                        self.tasks.append({"name": item['name'],"taskCode": item['taskCode'],"status":item['status']})
            else:
                self.logbuf.append(f"获取任务列表失败：{res['msg']}")
        except requests.RequestException as e:
            self.logbuf.append(f"获取任务列表失败：{e}")

    def joinTask(self,task):#加入任务
        data = {'taskCode':task['taskCode'],'lang':'zh_CN','platform':'0000000000000000','P00001':self.P00001}
        url = f"https://tc.vip.iqiyi.com/taskCenter/task/joinTask?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
            if res.get('code') == 'A00000':
                url = f"https://tc.vip.iqiyi.com/taskCenter/task/notify?{self.splice(data)}"
                self.logbuf.append(f"开始{task['name']}任务")
                self.notify(task)
            else:
                self.logbuf.append(f"开始{task['name']}任务失败：{res.get('msg','未知错误')}")
        except requests.RequestException as e:
            self.logbuf.append(f"开始{task['name']}任务失败：{e}")

    def notify(self,task):#通知
        data = {'taskCode':task['taskCode'],'lang':'zh_CN','platform':'0000000000000000','P00001':self.P00001}
        url = f"https://tc.vip.iqiyi.com/taskCenter/task/notify?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
        except requests.RequestException as e:
            self.logbuf.append(f"通知{task['name']}失败：{e}")

    def getTaskRewards(self,task):#领取奖励
        data = {'taskCode':task['taskCode'],'lang':'zh_CN','platform':'0000000000000000','P00001':self.P00001}
        url = f"https://tc.vip.iqiyi.com/taskCenter/task/getTaskRewards?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
            if res['msg'] == "成功":
                if res['code'] == 'A00000':
                    if res.get('dataNew'):
                        self.logbuf.append(f"{task['name']}已完成：{res['dataNew'][0]['name']} {res['dataNew'][0]['value']}")
                    else:
                        self.logbuf.append(f"{task['name']}任务可能未完成")
                else:
                    self.logbuf.append(f"{task['name']}任务失败：{res['msg']}")
            else:
                self.logbuf.append(f"{task['name']}任务失败：{res['msg']}")
        except requests.RequestException as e:
            self.logbuf.append(f"{task['name']}任务失败：{e}")

    def main(self):
        self.query_user_task()#获取任务列表
        for task in self.tasks:
            if task['status'] == 2:
                self.joinTask(task)
                time.sleep(0.5)
        time.sleep(10)
        self.query_user_task()#重新获取任务列表
        for task in self.tasks:
            if task['status'] == 4:
                self.notify(task)
        self.query_user_task()#重新获取任务列表
        for task in self.tasks:
            if task['status'] == 0:
                self.getTaskRewards(task)
                time.sleep(0.5)
            if task['status'] == 4:
                self.logbuf.append(f"{task['name']}任务：正在进行中，需要手动完成")
        if len(self.logbuf) == 1:
            self.logbuf.append('已全部完成')
        return '\n会员任务-'.join(self.logbuf)

class dailyTasks(init):#日常任务

    def __init__(self,user):
        init.__init__(self, user)
        #网页端任务列表
        self.web_task_list = [{'taskName':'访问热点首页','typeCode':'point','channelCode':'paopao_pcw','limitPerDay':1,'getRewardDayCount':0,'continuousRuleList':None},{'taskName':'每观看视频30分钟','typeCode':'point','channelCode':'view_pcw','limitPerDay':3,'getRewardDayCount':0,'continuousRuleList':None},{'taskName':'观看直播3分钟','typeCode':'point','channelCode':'live_3mins','limitPerDay':1,'getRewardDayCount':0,'continuousRuleList':None},{'taskName':'网页端签到','typeCode':'point','channelCode':'sign_pcw','limitPerDay':1,'getRewardDayCount':0,'continuousRuleList':['yes']}]

    def webTaskList(self):#获取网页端任务列表
        data = {'agenttype':'1','agentversion':'0','appKey':'basic_pcw','appver':'0','authCookie':self.P00001,'srcplatform':'1','typeCode':'point','userId':self.P00003,'verticalCode':'iQIYI'}
        data['sign'] = self.splice(data,'UKobMjDMsDoScuWOfp6F')
        url = f"https://community.iqiyi.com/openApi/task/list?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                self.web_task_list = []
                for task in res['data'][0]:
                    if task['limitPerDay'] > 0:
                        self.web_task_list.append({'taskName':task['channelName'],'typeCode':task['typeCode'],'channelCode':task['channelCode'],'limitPerDay':task['limitPerDay'],'getRewardDayCount':task['processCount'],'continuousRuleList':task['continuousRuleList']})
            else:
                self.logbuf.append(f"获取网页端任务列表失败：{res['message']}")
        except requests.RequestException as e:
            self.logbuf.append(f"获取网页端任务列表失败：{e}")

    def webTask(self,task):#完成网页端任务
        data = {"agenttype":"1","agentversion":"0","appKey":"basic_pca","appver":"0","authCookie":self.P00001,"channelCode":task['channelCode'],"dfp":self.dfp,"scoreType":"1","srcplatform":"1","typeCode":task['typeCode'],"userId":self.P00003,"user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36","verticalCode":"iQIYI"}
        data['sign'] = self.splice(data,"DO58SzN6ip9nbJ4QkM8H")
        if not task['continuousRuleList']: #如果不是连续任务，需要先完成任务再领取奖励
            url = f"https://community.iqiyi.com/openApi/task/complete?{self.splice(data)}"#完成任务
            try:
                res = requests.get(url)
                res.raise_for_status()
                res = res.json()
                if res['code'] == 'A00000':
                    url = f"https://community.iqiyi.com/openApi/score/getReward?{self.splice(data)}"#领取奖励
                    try:
                        res = requests.get(url)
                        res.raise_for_status()
                        res = res.json()
                        if res['code'] == 'A00000':
                            self.logbuf.append(f"{task['taskName']}：获得{res['data']['score']}点积分")
                        else:
                            self.logbuf.append(f"{task['taskName']}失败：{res['message']}")
                    except requests.RequestException as e:
                        self.logbuf.append(f"{task['taskName']}失败：{e}")
                else:
                    self.logbuf.append(f"{task['taskName']}失败：{res['message']}")
            except requests.RequestException as e:
                self.logbuf.append(f"{task['taskName']}失败：{e}")
        else:
            url = f"https://community.iqiyi.com/openApi/score/add?{self.splice(data)}"#连续任务
            try:
                res = requests.get(url)
                res.raise_for_status()
                res = res.json()
                if res['code'] == 'A00000':
                    if res['data'][0]['code'] == 'A0000':
                        quantity = res['data'][0]['score'] #积分
                        continued = res['data'][0]['continuousValue']#连续签到天数
                        self.logbuf.append(f"{task['taskName']}: 获得{quantity}点积分, 连续签到{continued}天")
                    else:
                        self.logbuf.append(f"{task['taskName']}失败：{res['data'][0]['message']}")
                else:
                    self.logbuf.append(f"{task['taskName']}失败：{res['message']}")
            except requests.RequestException as e:
                self.logbuf.append(f"{task['taskName']}失败：{e}")

    def main(self):
        self.webTaskList()
        for webtask in self.web_task_list:
            for _ in range(webtask['limitPerDay'] - webtask['getRewardDayCount']):
                self.webTask(webtask)
        if len(self.logbuf) == 1:
            self.logbuf.append('已全部完成')
        return '\n日常任务-'.join(self.logbuf)

class shake(init):#摇一摇
    def __init__(self,user,shareUserIds):
        init.__init__(self, user)
        self.shareUserIds = shareUserIds
        self.myid = ""
        self.isLottery = True # True 查询 False 抽奖

    def queryActivityTask(self):#获取摇一摇分享id
        data = {'P00001':self.P00001,'taskCode':'SHAKE_DRAW','messageId':self.message_id(),'appname':'sharingIncentive','_':round(time.time()*1000)}
        url = f"https://tc.vip.iqiyi.com/taskCenter/activity/queryActivityTask?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                self.myid = res['data']['shareUserId']
                if res['data']['status'] == 2:
                    self.logbuf.append("助力id：您已经被助力过了")
                elif res['data']['status'] == 6:
                    self.logbuf.append(f"助力id：{self.myid}")
            else:
                self.logbuf.append(f"助力id失败：{res['msg']}")
        except requests.RequestException as e:
            self.logbuf.append(f"助力id失败：{e}")

    def notifyActivity(self,shareUserId):#摇一摇助力
        data = {'P00001':self.P00001,'taskCode':'SHAKE_DRAW','messageId':self.message_id(),'appname':'sharingIncentive','shareUid':shareUserId,'_':round(time.time()*1000)}
        url = f"https://tc.vip.iqiyi.com/taskCenter/activity/notifyActivity?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                self.logbuf.append(f"助力：{res['msg']}")
            else:
                self.logbuf.append(f"助力失败：{res['msg']}")
        except requests.RequestException as e:
            self.logbuf.append(f"助力失败：{e}")

    def lottery_activity(self): #摇一摇抽奖
        data = {"app_k":"b398b8ccbaeacca840073a7ee9b7e7e6","app_v":"11.6.5","platform_id":10,"dev_os":"8.0.0","dev_ua":"FRD-AL10","net_sts":1,"qyid":self.qyid,"psp_uid":self.P00003,"psp_cki":self.P00001,"psp_status":3,"secure_p":"GPhone","secure_v":1,"req_sn":round(time.time()*1000)}
        if self.isLottery: #查询
            data["lottery_chance"] = 1
        url = f"https://iface2.iqiyi.com/aggregate/3.0/lottery_activity?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
            if res['code'] == 0:
                if self.isLottery:   #查询
                    self.isLottery = False
                    daysurpluschance = int(res.get('daysurpluschance','0'))
                    if daysurpluschance != 0:
                        return daysurpluschance
                    self.logbuf.append("抽奖：没有抽奖机会了")
                else:           #抽奖
                    if res['kv'].get('msg'):
                        self.logbuf.append(f"抽奖：{res['kv']['msg']}")
                    else:
                        if res['title'] == '影片推荐':
                            self.logbuf.append(f"抽奖：未中奖")
                        else:
                            self.logbuf.append(f"抽奖：{res['awardName']}")
            elif res['code'] == 3:
                self.logbuf.append("抽奖失败：Cookie失效")
            else:
                self.logbuf.append("抽奖失败：未知错误")
        except requests.RequestException as e:
            self.logbuf.append(f"抽奖失败：{e}")
        return 0

    def main(self):
        self.queryActivityTask()                                #获取摇一摇id
        for shareUserId in set(self.shareUserIds):
            if shareUserId != '' and shareUserId != self.myid:
                self.notifyActivity(shareUserId)                #摇一摇助力
        for _ in range(self.lottery_activity()):                #查询抽奖次数
            self.lottery_activity()                             #抽奖
            time.sleep(0.5)
        return '\n摇一摇-'.join(self.logbuf)

class lotto(init):#抽奖活动类
    def __init__(self,user):
        init.__init__(self, user)
        self.stime = 1643340                #默认开始时间
        self.etime = 4070880000             #默认结束时间
        self.ntime = round(time.time())     #当前时间
        self.isActivityTime = False         #活动时间标志
        self.giftlist = []                  #礼物列表
        self.actCode = ''

        self.header = {"Content-Type":"application/json;charset=UTF-8"}

    def lotto_giveTimes(self):#访问得次数
        data = {'P00001':self.P00001,'dfp':self.dfp,'qyid':self.qyid,'actCode':self.actCode,'timesCode':'browseWeb'}
        url = f"https://pcell.iqiyi.com/lotto/giveTimes?{self.splice(data)}"
        try:
            res = requests.post(url,headers=self.header)
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                self.logbuf.append("访问任务完成")
            else:
                self.logbuf.append(f"访问任务失败：{res['msg']}")
        except requests.RequestException as e:
                self.logbuf.append(f"访问任务失败：{e}")

    def lotto_queryTimes(self):#查询抽奖次数
        data = {'P00001':self.P00001,'dfp':self.dfp,'qyid':self.qyid,'actCode':self.actCode}
        url = f"https://pcell.iqiyi.com/lotto/queryTimes?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                if res['data']['times'] != 0:
                    return res['data']['times']
                else:
                    self.logbuf.append("抽奖：没有抽奖机会了")
            else:
                self.logbuf.append(f"查询抽奖次数失败：{res['msg']}")
        except requests.RequestException as e:
            self.logbuf.append(f"查询抽奖次数失败：{e}")
        return 0

    def lotto_lottery(self):#抽奖
        data = {'P00001':self.P00001,'dfp':self.dfp,'qyid':self.qyid,'actCode':self.actCode}
        url = f"https://pcell.iqiyi.com/lotto/lottery?{self.splice(data)}"
        try:
            res = requests.post(url,headers=self.header)
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                self.logbuf.append(f"抽奖：{res['data']['giftName']}+{res['data']['sendType']}")
            else:
                self.logbuf.append(f"抽奖失败：{res['msg']}")
        except requests.RequestException as e:
            self.logbuf.append(f"抽奖失败：{e}")

    def go_lottery(self):#去抽奖
        time.sleep(0.5)
        for _ in range(self.lotto_queryTimes()):
            self.lotto_lottery()
            time.sleep(0.5)

    def lotto_gift_records(self):#查询拥有的礼物
        data = {'P00001':self.P00001,'dfp':self.dfp,'qyid':self.qyid,'actCode':self.actCode,'pageNo':1,'pageSize':200}
        url = f"https://pcell.iqiyi.com/lotto/gift/records?{self.splice(data)}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            res = res.json()
            if res['code'] == 'A00000':
                giftlistbuf = []
                for prop in res['data']['records']:
                    propbuf = {'giftName': prop['giftName'],'ticket': prop['ticket']}
                    giftlistbuf.append(str(propbuf))
                giftlist = []
                for item in set(giftlistbuf):
                    gift = eval(item)
                    gift['count'] = giftlistbuf.count(item)
                    giftlist.append(gift)
                self.giftlist = giftlist
            else:
                self.logbuf.append(f"礼物查询失败：{res['msg']}")
        except requests.RequestException as e:
            self.logbuf.append(f"礼物查询失败：{e}")

    def activity_time(self,stime=None,etime=None):#活动时间
        if stime != None:
            self.stime = time.mktime(time.strptime(stime,"%Y-%m-%d %H:%M:%S"))
        if etime != None:
            self.etime = time.mktime(time.strptime(etime,"%Y-%m-%d %H:%M:%S"))
        if self.ntime > self.stime and self.ntime < self.etime:
            self.isActivityTime = True

#会员礼遇日
class vip_activity(lotto):

    def vip_gift(self):#礼物查询
        self.lotto_gift_records()#查询礼物列表
        if self.giftlist:
            buf = ['礼物查询：']
            for gift in self.giftlist:
                buf.append(f"--{gift['giftName']}+{gift['count']}")
            self.logbuf.append('\n'.join(buf))
        else:
            self.logbuf.append('礼物查询：还没有礼物哟')

    def main(self):
        month = time.strftime("%Y-%m-", time.localtime())
        self.activity_time(month + '27 11:00:00',month + '28 23:59:59') #活动时间 开始时间 结束时间
        if self.isActivityTime:
            self.actCode = "825dd6fad636f573"
            self.lotto_giveTimes()  #访问得次数
            self.go_lottery()       #去抽奖
            self.vip_gift()         #查询礼物列表
        else:
            self.logbuf.append("每月27/28日，当前不在活动时间内")
        return '\n会员礼遇日-'.join(self.logbuf)


if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json"), "r", encoding="utf-8") as f:
        datas = json.loads(f.read())
    _check_item = datas.get("IQIYI2", [])[0]
    print(IQIYI2(check_item=_check_item).main())
