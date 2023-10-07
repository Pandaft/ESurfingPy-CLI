from time import sleep

import requests
from psutil import net_io_counters

from .log import log


class Net:

    def __init__(self, upload: bool = False, download: bool = False):
        # assert upload or download
        self.upload = upload
        self.download = download

    @property
    def speed(self) -> float:
        """速率（MB/s)"""
        t1 = self.traffic
        sleep(1)
        t2 = self.traffic
        return round(t2 - t1, 2)

    @property
    def traffic(self) -> float:
        """流量（MB）"""
        t = 0
        net_io_counter = net_io_counters()
        if self.upload:
            t += net_io_counter.bytes_sent
        if self.download:
            t += net_io_counter.bytes_recv
        return round(t / 1024 / 1024, 2)


def is_online(retries=3, timeout=2):
    """判断是否已联网"""
    retries = 1 if retries < 1 else retries
    timeout = 1 if timeout < 1 else timeout
    for r in range(retries):
        try:
            requests.get(url="https://www.baidu.com/", timeout=timeout)
            log.info("当前网络正常")
            return True
        except requests.exceptions.Timeout:
            log.warning(f"当前网络异常（{r + 1}/{retries}）：请求超时")
        except Exception as exc:
            log.warning(f"网络请求异常（{r + 1}/{retries}）：{exc}")
        sleep(1)
    log.error("当前网络断开")
    return False
