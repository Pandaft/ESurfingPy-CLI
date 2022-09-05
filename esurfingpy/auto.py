import time
import psutil
from . import logs
from .esurfing import ESurfing

log = logs.log


def get_speed(obj_type: str) -> float:
    """获取当前上行或下行速率"""
    if obj_type == "upload":
        before = psutil.net_io_counters().bytes_sent
        time.sleep(1)
        delta = psutil.net_io_counters().bytes_sent - before
    elif obj_type == "download":
        before = psutil.net_io_counters().bytes_recv
        time.sleep(1)
        delta = psutil.net_io_counters().bytes_recv - before
    else:
        return 0
    return round(delta / 1024 / 1024, 2)  # 转为 x.xx (MB/s)


def get_traffic(obj_type: str) -> float:
    """获得当前上传或下载流量"""
    if obj_type == "upload":
        traffic = psutil.net_io_counters().bytes_sent
    elif obj_type == "download":
        traffic = psutil.net_io_counters().bytes_recv
    else:
        traffic = 0
    return traffic


def speed_mode(esf: ESurfing, mode: str, value: float, auto_stop: bool):
    """上行或下载速率低于指定值时自动重登校园网"""

    if mode == "upload":
        mode_str = "上传"
    elif mode == "download":
        mode_str = "下载"
    else:
        return

    log("尝试登录获取 signature ……")
    login_result = esf.login()
    if not login_result[0]:
        return log("登录失败")

    low_times = 0  # 低速次数
    seem_done = 0  # 低于 0.1 MB/s 时判定疑似传输完成的次数
    log_traffic = get_traffic(mode)

    while True:
        speed = get_speed(mode)
        now_traffic = get_traffic(mode) - log_traffic
        log(f"本次流量：{round(now_traffic / 1024 / 1024, 2)} MB\t"
            f"{mode_str}速度：{speed} MB/s\t"
            f"低速触发：{low_times}/10\t"
            f"完成触发：{seem_done}/10", rewrite=True)

        # 自动停止
        if auto_stop:
            if speed > 0.1:
                seem_done = 0
            else:
                # 速率低于 0.1 MB/s ，判定疑似传输完成
                seem_done += 1
                if seem_done == 11:
                    return log(f"检测到连续 10s {mode_str}速率低于 0.1 MB/s，已自动停止")

        # 限速检测
        if speed < value:
            # 速率低于指定值，疑似被限速
            low_times += 1
            if low_times == 11:
                log(f"检测到连续 10s {mode_str}速率低于 {value} MB/s，疑似被限速，重新登录中……")
                if not esf.logout():
                    return log("登出失败")
                if not esf.login():
                    return log("登录失败")
                low_times, seem_done = 0, 0
                log_traffic = get_traffic(mode)
        else:
            # 速率高于指定值
            low_times = 0
            seem_done = 0


def traffic_mode(esf: ESurfing, mode: str, value: float):
    """上传或下载流量达到指定值时自动重登校园网"""

    if mode == "3":
        mode = "upload"
        mode_str = "上传"
    elif mode == "4":
        mode = "download"
        mode_str = "下载"
    else:
        return

    log("首次登录尝试获取 signature ……")
    if not esf.login():
        return log(f"登录失败")

    log_traffic = get_traffic(mode)
    while True:
        delta = round((get_traffic(mode) - log_traffic) / 1024 / 1024, 2)
        speed = get_speed(mode_str)
        log(f"{mode_str}速率：{speed} MB/s  流量触发：{delta}/{value} MB", rewrite=True)
        if delta >= value:
            log()
            log("重新登录中")
            if not esf.logout():
                return log("登出失败")
            if not esf.logout()[0]:
                return log(f"登录失败")
            log_traffic = get_traffic(mode)


def interval_mode(esf: ESurfing, value):
    """间隔指定的时间自动重登校园网"""

    log("首次登录尝试获取 signature ……")
    first_login = esf.login()
    if not first_login[0]:
        return log(f"登录失败：{first_login}")

    time_cal = 0
    while True:
        log(f"即将于 {value - time_cal}s 后重新登录", rewrite=True)
        time.sleep(1)
        if value - time_cal == 0:
            print()
            log("正在重新登录\n", rewrite=True)
            if not esf.logout()[0]:
                return log("登录失败")
            if not esf.login()[0]:
                return log("登出失败")
            time_cal = 0
        else:
            time_cal += 1


def manual_mode(esf: ESurfing):
    """手动按回车后自动重登校园网"""

    log("首次登录尝试获取 signature ……")
    if not esf.login():
        return log("登录失败")

    while True:
        input(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 按回车键以重新登录校园网")
        esf.logout()
        if not esf.login():
            return log(f"登录失败")


def relogin(esf: ESurfing, mode: str, value: float, autostop: bool):
    """
        uls, upload_speed     - 上行速率低于指定值时自动重登校园网
        dls, download_speed   - 下载速率低于指定值时自动重登校园网
        ult, upload_traffic   - 上传流量达到指定值时自动重登校园网
        dlt, download_traffic - 下载流量达到指定值时自动重登校园网
        itv, interval         - 间隔指定的时间自动重登校园网
        mul, manual           - 手动按回车后自动重登校园网
    """
    while True:
        if mode not in ["uls", "dls", "ult", "dlt", "itv", "mul"]:
            print("触发模式：\n"
                  "uls, upload_speed     - 上行速率低于指定值时自动重登校园网\n"
                  "dls, download_speed   - 下载速率低于指定值时自动重登校园网\n"
                  "ult, upload_traffic   - 上传流量达到指定值时自动重登校园网\n"
                  "dlt, download_traffic - 下载流量达到指定值时自动重登校园网\n"
                  "itv, interval         - 间隔指定的时间自动重登校园网\n"
                  "mul, manual           - 手动按回车后自动重登校园网")
            mode = input("请选择正确的触发模式：")
            if mode in ["uls", "dls", "ult", "dlt", "itv", "mul"]:
                break
            else:
                continue
        else:
            if mode != "mul":
                while True:
                    try:
                        value = float(value)
                        break
                    except:
                        value = input("请输入正确的触发值（单位：MB/s, MB, s）：")
                        continue

    if mode in ["uls", "dls"]:
        speed_mode(esf, mode, value, autostop)
    elif mode in ["ult", "dlt"]:
        traffic_mode(esf, mode, value)
    elif mode == "itv":
        interval_mode(esf, value)
    elif mode == "mul":
        manual_mode(esf)
    return
