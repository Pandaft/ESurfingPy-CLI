import re
import json
import time
import requests
from . import ocr, rsa, logs

DEFAULT_ESURFING_URL = "enet.10000.gd.cn:10001"


class ESurfing:

    def __init__(self,
                 account: str,
                 password: str = "",
                 signature: str = "",
                 esurfingurl: str = DEFAULT_ESURFING_URL,
                 wlanacip: str = "",
                 wlanuserip: str = "",
                 verbose: bool = True):
        """实例化"""
        self.account = account
        self.password = password
        self.signature = signature
        if not all([esurfingurl, wlanacip, wlanuserip]):
            _, self.esurfingurl, self.wlanacip, self.wlanuserip, = get_parameters()
        else:
            self.esurfingurl = esurfingurl
            self.wlanacip = wlanacip
            self.wlanuserip = wlanuserip
        self.verbose = verbose

    def login(self):
        """登录"""
        login_result = login(account=self.account,
                             password=self.password,
                             esurfingurl=self.esurfingurl,
                             wlanacip=self.wlanacip,
                             wlanuserip=self.wlanuserip,
                             verbose=self.verbose)
        if login_result[0]:
            self.signature = login_result[1]
        return login_result

    def logout(self):
        """登出"""
        return logout(account=self.account,
                      password=self.password,
                      signature=self.signature,
                      esurfingurl=self.esurfingurl,
                      wlanacip=self.wlanacip,
                      wlanuserip=self.wlanuserip,
                      verbose=self.verbose)


def get_parameters(verbose: bool = False):
    """
    获取 esurfingurl, wlanacip, wlanuserip 参数
    本机未登录校园网时才可通过此方法获取上述参数
    """
    try:
        response = requests.get(url="http://189.cn/")
        esurfingurl = re.search("http://(.+?)/", response.url).group(1)
        wlanacip = re.search("wlanacip=(.+?)&", response.url).group(1)
        wlanuserip = re.search("wlanuserip=(.+)", response.url).group(1)
        return True, esurfingurl, wlanacip, wlanuserip
    except Exception as exc:
        if verbose:
            logs.log(f"获取参数失败：{exc}")
        return False, None, None, None


def login(account: str, password: str,
          esurfingurl: str = DEFAULT_ESURFING_URL, wlanacip: str = "", wlanuserip: str = "",
          verbose: bool = True):
    """
    登录校园网
    account, password 必填参数；
    esurfingurl, wlanacip, wlanuserip 选填参数，本机登录且未登录时可自动获取；
    verbose: 选填参数，输出过程。
    """

    # 日志
    def log(text):
        if verbose:
            logs.log(text)
        return text

    # 记录
    log_data = {
        "time": time.time(),  # 开始时间
        "times": 0  # 验证码识别错误次数（不符合条件的不算）
    }

    # 判断是否缺少参数：account, password
    if not all([account, password]):
        return False, log("登录失败：缺少 Account, Password 参数")

    # 判断是否缺少参数：esurfingurl, wlanacip, wlanuserip
    if not all([esurfingurl, wlanacip, wlanuserip]):
        log("缺少 ESurfingUrl, WlanACIP, WlanUserIP 参数，尝试获取中……")
        success, esurfingurl, wlanacip, wlanuserip = get_parameters()
        if not success:
            return False, log("获取失败")
        log("获取成功：")
        log(f"  - ESurfingUrl: {esurfingurl}")
        log(f"  - WlanACIP: {wlanacip}")
        log(f"  - WlanUserIP: {wlanuserip}")

    while True:
        session = requests.session()

        # 访问认证登录页面
        try:
            log("正在请求获取登录页面...")
            resp = session.get(
                url=f"http://{esurfingurl}/qs/index_gz.jsp?wlanacip={wlanacip}&wlanuserip={wlanuserip}"
            )
            log("请求获取登录页面成功")
        except Exception as exc:
            return False, log(f"请求获取登录页面失败：{exc}")

        # 正则匹配验证码网址
        try:
            log('正在获取验证码网址...')
            vcode_path = re.search('/common/image_code\.jsp\?time=\d+', str(resp.content)).group()
            vcode_url = f'http://{esurfingurl}{vcode_path}'
        except Exception as exc:
            return False, log(f"获取验证码网址失败：{exc}")

        while True:
            # 获取并保存验证码
            try:
                log("正在获取验证码图片...")
                resp = session.get(url=vcode_url)
                log("获取验证码图片成功")
            except Exception as exc:
                return False, log(f"请求获取验证码失败：{exc}")

            # 识别验证码
            try:
                log("正在识别验证码...")
                log_time = time.time()
                ocr_succeed, ocr_result = ocr.ocr_image(resp.content)
                time_taken = round(time.time() - log_time, 2)

                # 识别失败
                if not ocr_succeed:
                    return False, log(f"识别验证码失败：{ocr_result}")
                if len(ocr_result) < 4:
                    log("验证码识别结果不符合条件，重新获取新的验证码...")
                    continue

                # 识别成功
                ocr_result = ocr_result[0:4]
                log(f'识别验证码成功：{ocr_result}  耗时：{time_taken}s')
                break
            except Exception as exc:
                return False, log(f"识别验证码失败：{exc}")

        # 计算 loginKey
        try:
            log_time = time.time()
            log('正在计算 loginKey ...')
            login_key = rsa.encrypt(account, password, ocr_result)
            time_taken = round(time.time() - log_time, 2)
            log(f"完成计算，耗时：{time_taken}s")
        except Exception as exc:
            return False, log(f"计算 loginKey 失败：{exc}")

        # 发送登录请求
        try:
            log('正在发送登录请求...')
            resp = requests.post(
                url=f'http://{esurfingurl}/ajax/login',
                headers={
                    "Cookie": f"'loginUser={account}; JSESSIONID={session.cookies.get('JSESSIONID')}'",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
                data=f"loginKey={login_key}&wlanuserip={wlanuserip}&wlanacip={wlanacip}"
            )
            if not resp.ok:
                return False, log(f"登录请求回应异常，HTTP 状态码：{resp.status_code}，返回文本：{resp.text}")
        except Exception as exc:
            return False, log(f'发送登录请求失败：{exc}')

        # 判断登录结果
        result_code = json.loads(resp.text)['resultCode']
        result_info = json.loads(resp.text)['resultInfo']

        # 登录成功
        if result_code == '0':
            time_taken = round(time.time() - log_data['time'], 2)
            log(f'登录成功，总耗时 {time_taken}s，失败 {log_data["times"]} 次')
            log(f'signature: {resp.cookies["signature"]}')
            return True, resp.cookies['signature']

        # 重复登录
        elif result_code == '13002000':
            time_taken = round(time.time() - log_data['time'], 2)
            log(f'重复登录，总耗时 {time_taken}s，失败 {log_data["times"]} 次')
            log(f'signature: {resp.cookies["signature"]}')
            return True, resp.cookies['signature']

        # 验证码错误
        elif result_code == '11063000':
            log(result_info)
            log_data['times'] += 1
            continue

        # 请求认证超时
        elif result_code == '13005000':
            log(result_info)
            log_data['times'] += 1
            return False, log("认证超时")

        # 禁止网页认证
        elif result_code == '13018000':
            return False, log(result_info)

        # 其他情况
        else:
            return False, log(f"登录失败，返回码：{result_code}  信息：{result_info}")


def logout(account: str,
           wlanacip: str, wlanuserip: str, esurfingurl: str = DEFAULT_ESURFING_URL,
           password: str = "", signature: str = "",
           verbose: bool = True):
    """
    登出校园网
    account 必填参数；
    esurfingurl, wlanacip, wlanuserip 必填参数；
    password, signature 至少填一项参数；
    verbose: 选填参数，输出过程。
    """

    # 日志
    def log(text):
        if verbose:
            logs.log(text)
        return text

    # 记录
    log_data = {
        "time": time.time(),  # 开始时间
        "times": 0  # 验证码识别错误次数（不符合条件的不算）
    }

    # 判断是否缺少参数：password / signature
    if not any([password, signature]):
        return False, log("登出失败：缺少 Password, Signature 任一参数")

    # 判断是否缺少参数：esurfingurl, wlanacip, wlanuserip
    if not all([esurfingurl, wlanacip, wlanuserip]):
        return False, log("登出失败：缺少 ESurfingUrl, WlanACIP, WlanUserIP 参数")

    # 缺少 signature
    if not signature:
        # 尝试通过登录获取
        log('缺少 signature 参数，正在尝试通过登录获取该参数...')
        login_result = login(account, password, esurfingurl, wlanacip, wlanuserip, verbose)

        # 登录失败
        if not login_result[0]:
            return False, log("登出失败：缺少 signature 参数，且尝试通过登录获取失败")

        # 登录成功
        signature = login_result[1]
        log(f'获取成功，signature: {signature}')

    # 请求登出
    try:
        log('正在发送登出请求...')
        resp = requests.post(
            url=f'http://{esurfingurl}/ajax/logout',
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0',
                'Cookie': f'signature={signature}; loginUser={account}',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data=f"wlanuserip={wlanuserip}&wlanacip={wlanacip}"
        )
        if not resp.ok:
            return False, log(f"登出请求回应异常，HTTP 状态码：{resp.status_code}，返回文本：{resp.text}")
    except Exception as exc:
        return False, log(f'发送登出请求失败：{exc}')

    # 判断登出结果
    result_code = json.loads(resp.text)['resultCode']
    result_info = json.loads(resp.text)['resultInfo']

    # 登出成功 / 重复登出
    if result_code == '0':
        time_taken = round(time.time() - log_data["time"], 2)
        return True, log(f'登出成功，耗时 {time_taken}s')

    # 登出失败
    return False, log(f'登出失败，返回码：{result_code}  信息：{result_info}')
