import socket
from time import sleep

from psutil import net_io_counters


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


def is_networked():
    """判断是否已联网"""
    try:
        socket.create_connection(("114.114.114.114", 53), timeout=2)
        return True
    except TimeoutError:
        pass
    return False
