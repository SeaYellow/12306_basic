import requests
from json import loads
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from PIL import Image

head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
}
now_session = requests.Session()
now_session.verify = False

username = "huanghai200911@163.com"
password = ""

locate = {
    '1': '44,44,',
    '2': '114,44,',
    '3': '185,44,',
    '4': '254,44,',
    '5': '44,124,',
    '6': '114,124,',
    '7': '185,124,',
    '8': '254,124,',
}

disable_warnings(InsecureRequestWarning)


class Login:
    def getContactsMsg(self):
        # 获取联系人信息
        passengerUrl = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
        respPassenger = now_session.get(passengerUrl, headers=head)
        passengerMsg = loads(respPassenger.content)
        if passengerMsg["httpstatus"] == 200:
            personMsgs = passengerMsg["data"]["normal_passengers"]
            for personMsg in personMsgs:
                print("常用联系人信息：%s" % personMsg)

    def login(self):
        try:
            yzdata = {
                'appid': 'otn'
            }
            tk_url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
            validateMsg = now_session.post(tk_url, data=yzdata, headers=head)
            print(validateMsg.content)
            validateMsgJson = loads(validateMsg.content)

            print('-----------------验证码验证-----------------')
            resp1 = now_session.get(
                'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.8430851651301317',
                headers=head)
            print("status_code : %d " % resp1.status_code)

            with open('../../temp/code.png', 'wb') as f:
                f.write(resp1.content)
            # 展示验证码图片，会调用系统自带的图片浏览器打开图片，线程阻塞
            try:
                im = Image.open('../../temp/code.png')
                im.show()
                # 关闭，只是代码关闭，实际上图片浏览器没有关闭，但是终端已经可以进行交互了(结束阻塞)
                im.close()
            except BaseException as error:
                print("验证图片打开异常：%s" % error.__str__())
            print('请输入验证码坐标代号：')
            code = input()
            write = code.split(',')
            codes = ''
            for i in write:
                codes += locate[i]
            data = {
                'answer': codes,
                'login_site': 'E',
                'rand': 'sjrand'
            }
            print("login parameter : %s" % data)

            resp = now_session.post('https://kyfw.12306.cn/passport/captcha/captcha-check', headers=head, data=data)

            print("验证码验证返回信息：%s" % resp.content)

            html = loads(resp.content)
            if html['result_code'] == '4':
                print('验证码校验成功！')
                print('-----------------登录中-----------------')
                login_url = 'https://kyfw.12306.cn/passport/web/login'
                user = {
                    'username': username,
                    'password': password,
                    'appid': 'otn'
                }
                resp2 = now_session.post(login_url, headers=head, data=user)
                html = loads(resp2.content)
                print(html)
                if html['result_code'] == 0:
                    print('登陆成功！')
                    yzdata = {
                        'appid': 'otn'
                    }
                    tk_url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
                    resp3 = now_session.post(tk_url, data=yzdata, headers=head)
                    resp3Json = resp3.json()
                    if resp3Json["result_code"] == 0:
                        print('-----------------第一次验证通过-----------------')
                        newapptk = resp3Json['newapptk']
                        yz2data = {
                            'tk': newapptk
                        }
                        client_url = 'https://kyfw.12306.cn/otn/uamauthclient'
                        resp4 = now_session.post(client_url, data=yz2data, headers=head)
                        resp4Json = resp4.json()
                        if resp4Json["result_code"] == 0:
                            print('-----------------第二次验证通过-----------------')
                            return True
                        else:
                            print('-----------------第二次验证不通过，请重新登陆-----------------')
                            return False
                    else:
                        print('-----------------第一次验证不通过，请重新登陆-----------------')
                        return False
                else:
                    print('登陆失败！')
                    return False
            else:
                print('验证码校验失败，正在重新请求页面...')
                return False
        except BaseException as error:
            print(error.__str__())
            return False


if __name__ == '__main__':
    login = Login()
    while True:
        flg = login.login()
        if flg:
            break
    print('-----------------开始获取联系人信息-----------------')
    login.getContactsMsg()
