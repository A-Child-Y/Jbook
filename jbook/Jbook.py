import http.cookiejar
import requests
import re
from fake_useragent import UserAgent
import time


class JSObject(object):
    def __init__(self):
        # 简书账号
        self.username = '简书账号'
        self.password = '简书密码.'

        # 极验证用户账号
        self.name = '极验账号'
        self.word = '极验密码'

        # 极验开发者账号
        self.money_name = 'yigexiaohai'

        self.headers = {
            'User-Agent': UserAgent().random
        }

        self.session = requests.session()
        self.session.cookies = http.cookiejar.MozillaCookieJar('jBook_cookie.text')
        self.url = 'https://www.jianshu.com'
        self.sign_in_url = 'https://www.jianshu.com/sign_in'
        self.captcha_url = 'https://www.jianshu.com/captchas/new?t={}-cog'.format(str(time.time()).replace('.', '')[0:13])
        self.api_url = 'http://jiyanapi.c2567.com/shibie?gt={}&challenge={}' \
                       '&referer={}&user={}&pass={}&devuser={}&return=json&model=3&format=utf8'
        self.login_url = 'https://www.jianshu.com/sessions'
        self.data_url = 'https://www.jianshu.com/'

    def sign_in(self):
        """
        从网页源代码中，拿到 authenticity_token 参数
        :return: authenticity_token 参数
        """
        try:
            response = self.session.get(url=self.sign_in_url, headers=self.headers)
            if response.status_code == 200:
                print('成功访问网页源代码，开始获取 authenticity_token 参数 ')
        except Exception as e:
            print('访问源代码状态码异常：{}'.format(e))
        else:
            res = re.compile(r'name="authenticity_token" value="(.*?)" />', re.S)
            authenticity_token = re.search(res, response.text).group(1)
            return authenticity_token

    def captcha(self):
        """
        访问验证码，拿到 gt，challenge
        :return: gt，challenge
        """
        try:
            response = self.session.get(url=self.captcha_url, headers=self.headers)
            if response.status_code == 200:
                print('成功访问验证码，开始获取，gt，challenge 参数')
        except Exception as e:
            print('访问验证码状态码异常：{}'.format(e))
        else:
            res = response.json()
            gt = res['gt']
            challenge = res['challenge']
            return gt, challenge

    def api(self):
        """
        拿到 gt，challenge，破解验证码
        :return: 破解完成的 challenge， validate
        """
        gt, challenge = self.captcha()
        try:
            response = self.session.get(url=self.api_url.format(gt, challenge, self.url, self.name,
                                                                self.word, self.money_name),
                                        headers=self.headers).json()
            if response['status'] == 'ok':
                print('访问成功， 拿到 challenge， validate')
                challenge = response['challenge']
                validate = response['validate']
                return challenge, validate
            elif response['status'] == 'no':
                print('行为异常，请重新访问')
                return None
            elif response['status'] == 'stop':
                print('用户异常， 请重新注册')
                return None
        except Exception as e:
            print('破解状态码异常：{}'.format(e))

    def login(self):
        """
        拼接参数， 破解登录，拿到cookie
        :return:
        """
        authenticity_token = self.sign_in()
        gt, challenge1 = self.captcha()
        challenge2, validate = self.api()
        data = {
            'utf8': '√',
            'authenticity_token': authenticity_token,
            'session[email_or_mobile_number]': self.username,
            'session[password]': self.password,
            'session[oversea]': 'false',
            'captcha[validation][challenge]': challenge2,
            'captcha[validation][gt]': gt,
            'captcha[validation][validate]': validate,
            'captcha[validation][seccode]': validate + "|jordan",
            'session[remember_me]': 'true'
        }
        self.session.post(url=self.login_url, data=data, headers=self.headers)
        self.session.cookies.save(ignore_discard=True, ignore_expires=True)

    def data(self):
        """
        用本地cookie 访问个人简书首页，拿到个人昵称
        :return:
        """
        self.session.cookies.load('jBook_cookie.text', ignore_discard=True, ignore_expires=True)
        try:
            response = self.session.get(url=self.data_url, headers=self.headers)
            if response.status_code == 200:
                print('成功登陆首页，开始获取数据')
        except Exception as e:
            print('访问异常：{}'.format(e))
        else:
            res = re.compile(r'nickname":"(.*?)",', re.S)
            name = re.search(res, response.text).group(1)
            print('')
            print('简书个人昵称：', name)
            print('')

    def run(self):
        """
        login启动函数
        :return:
        """
        print('开始破解简书登录')
        self.login()
        print('破解完成！')
        self.start()

    def start(self):
        """
        data启动函数
        :return:
        """
        print('开始获取数据')
        self.data()
        print('获取数据完成！')


if __name__ == '__main__':
    joker = JSObject()
    joker.run()

