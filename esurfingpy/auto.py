import time

from . import log
from .esurfing import ESurfing
from .net import Net, is_online


def network(esf: ESurfing, interval: int = 5, threshold: int = 3):
    """断网时自动重登校园网"""

    # 最小间隔时间为 1 秒
    if int(interval) < 1:
        interval = 1

    while True:

        # 检测网络
        if not is_online(retries=threshold):
            if not esf.login():
                return log.error("登录失败")

        time.sleep(interval)


def speed_mode(esf: ESurfing, mode: str, value: float, auto_stop: bool):
    """上行或下载速率低于指定值时自动重登校园网"""

    if mode == "uls":
        mode_str = "上传"
        net = Net(upload=True)
    elif mode == "dls":
        mode_str = "下载"
        net = Net(download=True)
    else:
        return log.error("模式参数错误")

    # 获取 signature 参数
    if not esf.signature:
        log.warning("尝试登录获取 signature ……")
        success, message = esf.login()
        if not success:
            return log.error(f"登录失败：{message}")

    low_times = 0  # 低速次数
    seem_done = 0  # 低于 0.1 MB/s 时判定疑似传输完成的次数
    log_traffic = net.traffic

    while True:
        speed = net.speed
        now_traffic = round(net.traffic - log_traffic, 2)
        log.info(f"本次流量：{now_traffic} MB\t"
                 f"{mode_str}速度：{speed} MB/s\t"
                 f"低速触发：{low_times}/10\t"
                 f"完成触发：{seem_done}/10")

        # 自动停止
        if auto_stop:
            if speed > 0.1:
                seem_done = 0
            else:
                # 速率低于 0.1 MB/s ，判定疑似传输完成
                seem_done += 1
                if seem_done == 11:
                    return log.warning(f"检测到连续 10s {mode_str}速率低于 0.1 MB/s，已自动停止")

        # 限速检测
        if speed < value:
            # 速率低于指定值，疑似被限速
            low_times += 1
            if low_times == 11:
                log.warning(f"检测到连续 10s {mode_str}速率低于 {value} MB/s，疑似被限速，重新登录中……")
                if not esf.logout():
                    return log.error("登出失败")
                time.sleep(2.5)  # 避免认证超时
                if not esf.login():
                    return log.error("登录失败")
                low_times, seem_done = 0, 0
                log_traffic = net.traffic
        else:
            # 速率高于指定值
            low_times = 0
            seem_done = 0


def traffic_mode(esf: ESurfing, mode: str, value: float):
    """上传或下载流量达到指定值时自动重登校园网"""

    if mode == "ult":
        mode_str = "上传"
        net = Net(upload=True)
    elif mode == "dlt":
        mode_str = "下载"
        net = Net(download=True)
    else:
        return log.error("模式参数错误")

    # 获取 signature 参数
    if not esf.signature:
        log.warning("首次登录尝试获取 signature ……")
        if not esf.login():
            return log.error(f"登录失败")

    log_traffic = net.traffic
    while True:
        delta = round(net.traffic - log_traffic, 2)
        speed = net.speed
        log.info(f"{mode_str}速率：{speed} MB/s  "
                 f"流量触发：{delta}/{value} MB")
        if delta >= value:
            log.warning("重新登录中")
            if not esf.logout():
                return log.error("登出失败")
            time.sleep(2.5)  # 避免认证超时
            if not esf.login()[0]:
                return log.error(f"登录失败")
            log_traffic = net.traffic


def interval_mode(esf: ESurfing, value):
    """间隔指定的时间自动重登校园网"""

    log.warning("首次登录尝试获取 signature ……")
    first_login = esf.login()
    if not first_login[0]:
        return log.error(f"登录失败：{first_login}")

    time_cal = 0
    while True:
        log.info(f"即将于 {value - time_cal}s 后重新登录")
        time.sleep(1)
        if value - time_cal == 0:
            log.warning("正在重新登录")
            if not esf.logout()[0]:
                return log.error("登录失败")
            time.sleep(2.5)  # 避免认证超时
            if not esf.login()[0]:
                return log.error("登出失败")
            time_cal = 0
        else:
            time_cal += 1


def manual_mode(esf: ESurfing):
    """手动按回车后自动重登校园网"""

    log.warning("首次登录尝试获取 signature ……")
    if not esf.login():
        return log.error("登录失败")

    while True:
        input(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 按回车键以重新登录校园网")
        esf.logout()
        if not esf.login():
            return log.error(f"登录失败")


def relogin(esf: ESurfing, mode: str, value: float, auto_stop: bool):
    """
        net, network          - 当网络断开时自动登录校园网
        uls, upload_speed     - 上行速率低于指定值时自动重登校园网
        dls, download_speed   - 下载速率低于指定值时自动重登校园网
        ult, upload_traffic   - 上传流量达到指定值时自动重登校园网
        dlt, download_traffic - 下载流量达到指定值时自动重登校园网
        itv, interval         - 间隔指定的时间自动重登校园网
        mul, manual           - 手动按回车后自动重登校园网
    """

    # 网络模式
    if mode == "net":
        return network(esf, 5, int(value))

    # 速率模式
    elif mode in ["uls", "dls"]:
        return speed_mode(esf, mode, value, auto_stop)

    # 流量模式
    elif mode in ["ult", "dlt"]:
        return traffic_mode(esf, mode, value)

    # 间隔模式
    elif mode == "itv":
        return interval_mode(esf, value)

    # 手动模式
    elif mode == "mul":
        return manual_mode(esf)

    # 模式错误
    return log.error("模式参数错误")
