# -*- coding: utf-8 -*-
import json
import os

import requests
import subprocess

from dailycheckin import CheckIn


class FMAPP(CheckIn):
    name = "Fa米家"

    def __init__(self, check_item):
        self.check_item = check_item

    @staticmethod
    def sign(headers):
        try:
            url = "https://fmapp.chinafamilymart.com.cn/api/app/market/member/signin/sign"
            response = requests.post(url=url, headers=headers).json()
            code = response.get("code")
            if code == "200":
                data = response.get("data", {})
                next_type = data.get("nextGrantType")
                cur_type = data.get("currentGrantType")
                type_map = {
                    1: "发米粒",
                    7: '会员成长值'
                }
                msg = (
                    f"本次获得{data.get('currentNumber')}个{type_map[cur_type]}, "
                    f"在坚持{data.get('nextDay')}天即可获得{data.get('nextNumber')}个{type_map[next_type]}, "
                    f"签到{data.get('lastDay')}天可获得{data.get('lastNumber')}个发米粒"
                )
            else:
                msg = response.get("message")
        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "签到信息", "value": msg}
        return msg

    @staticmethod
    def user_info(headers):
        try:
            url = "https://fmapp.chinafamilymart.com.cn/api/app/member/info"
            response = requests.post(url=url, headers=headers).json()
            code = response.get("code")
            if code == "200":
                data = response.get("data", {})
                msg = data.get("nickName")
            else:
                msg = response.get("message")
        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "帐号信息", "value": msg}
        return msg

    @staticmethod
    def mili_count(headers):
        try:
            url = "https://fmapp.chinafamilymart.com.cn/api/app/member/v1/mili/service/detail"
            response = requests.post(url=url, headers=headers, data=json.dumps({"pageSize": 10, "pageNo": 1})).json()
            code = response.get("code")
            if code == "200":
                data = response.get("data", {})
                msg = data.get("miliNum")
            else:
                msg = response.get("message")
        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "米粒数量", "value": msg}
        return msg

    @staticmethod
    def get_local_city():
        pro = subprocess.run(['curl', 'cip.cc'], capture_output=True)
        ret = pro.stdout.decode().strip()
        lines = ret.split('\n')
        for line in lines:
            if '地址' in line:
                tt = line.split(' ')
                return tt[len(tt) - 1]
        return '成都'

    @staticmethod
    def mili_change_list(headers):
        try:
            url = "https://fmapp.chinafamilymart.com.cn/api/app/oms/v2/mili/service/category/product/list"
            data = {
                'cityCd': FMAPP.get_local_city(),
                'couponIds': [
                    '11720', '11713', '11721', '11714', '11662', '11622', '11715', '11716', '11717', '12014', '11718', '11719', '12016', '12011', '12012', '12013'
                ]
            }
            response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()
            code = response.get("code")
            if code == "200":
                data = response.get("data", {})
                msg = '\n==============\n'
                for item in data:
                    cnt_left = item['inventoryNum'] - item['gainNum']
                    if cnt_left > 0:
                        msg += f'名称: {item["name"]};\n尊享米粒价: {item["zxPrice"]};\n集享米粒价: {item["jxPrice"]},\n原价: {item["price"]};\n剩余数量: {cnt_left};\n==============\n'
            else:
                msg = response.get("message")
        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "米粒兑换信息", "value": msg}
        return msg

    @staticmethod
    def member_info(headers):
        try:
            url = "https://fmapp.chinafamilymart.com.cn/api/app/member/personal/center"
            response = requests.post(url=url, headers=headers, data=json.dumps({"cityName": "成都", "position": 4})).json()
            code = response.get("code")
            if code == "200":
                data = response.get("data", {})
                msg = '\n==============\n会员积分:{}/{};\n会员到期时间:{};\n本月消费:{};\n本月节省:{};\n本月积分:{};\n全部积分:{};\n米粒统计:共计{}个米粒,其中{}个将于{}过期;\n=============='.format(
                    data.get("mifen"),
                    data.get("mifenTotal"),
                    data.get("zxEndDate"),
                    data.get("monthInvoiceAmt"),
                    data.get("monthSaveAmt"),
                    data.get("monthTotPoints"),
                    data.get("familyTotalPoint"),
                    data.get("miliCount"),
                    data.get("expireMiliNum"),
                    data.get("expireDate"))
            else:
                msg = response.get("message")
        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "会员信息", "value": msg}
        return msg

    def main(self):
        token = self.check_item.get("token")
        cookie = self.check_item.get("cookie")
        blackbox = self.check_item.get("blackbox")
        device_id = self.check_item.get("device_id")
        fmversion = self.check_item.get("fmversion", "2.2.3")
        fm_os = self.check_item.get("os", "ios")
        useragent = self.check_item.get("useragent", "Fa")
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-Hans;q=1.0",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "Host": "fmapp.chinafamilymart.com.cn",
            "Content-Type": "application/json",
            "loginChannel": "app",
            "token": token,
            "fmVersion": fmversion,
            "deviceId": device_id,
            "User-Agent": useragent,
            "os": fm_os,
            "cookie": cookie,
            "blackBox": blackbox,
        }
        sign_msg = self.sign(headers=headers)
        name_msg = self.user_info(headers=headers)
        mili_msg = self.mili_count(headers=headers)
        member_info = self.member_info(headers=headers)
        mili_change_msg = self.mili_change_list(headers=headers)
        msg = [name_msg, sign_msg, mili_msg, member_info, mili_change_msg]
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json"), "r", encoding="utf-8") as f:
        datas = json.loads(f.read())
    _check_item = datas.get("FMAPP", [])[0]
    print(FMAPP(check_item=_check_item).main())
