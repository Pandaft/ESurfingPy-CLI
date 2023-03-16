import os
import time

import click

from . import esurfing
from .__version__ import __version__, __date__
from .auto import relogin
from .gui import Gui
from .ocr import ocr_image

DEFAULT_ESURFING_URL = "enet.10000.gd.cn:10001"


@click.group()
def cli():
    """基于 Python 实现登录和登出广东天翼校园网网页认证通道的命令行工具。"""
    pass


@cli.command(name="gui")
def cli_gui():
    """启动图形界面"""
    Gui().run()


@cli.command(name="login")
@click.option('-u', '--esurfing-url', default=DEFAULT_ESURFING_URL, show_default=True, help='校园网登录网址')
@click.option('-c', '--wlan-acip', help='认证服务器IP')
@click.option('-r', '--wlan-userip', help='登录设备IP')
@click.option('-a', '--account', prompt='账号', help='账号')
@click.option('-p', '--password', prompt='密码', help='密码')
@click.option('-v', '--verbose', type=bool, default=True, show_default=True, help='输出详细过程')
def cli_login(esurfing_url, wlan_acip, wlan_userip, account, password, verbose):
    """登录校园网"""
    # account, password 必填参数；
    # esurfing_url, wlan_acip, wlan_userip 选填参数，本机登录且未登录时可自动获取；
    # verbose: 选填参数，输出过程。
    return esurfing.login(esurfingurl=esurfing_url, wlanacip=wlan_acip, wlanuserip=wlan_userip,
                          account=account, password=password, verbose=verbose)


@cli.command(name="logout")
@click.option('-u', '--esurfing-url', default=DEFAULT_ESURFING_URL, help='校园网登录网址')
@click.option('-c', '--wlan-acip', prompt='认证服务器IP', help='认证服务器IP')
@click.option('-r', '--wlan-userip', prompt='登录设备IP', help='登录设备IP')
@click.option('-a', '--account', prompt='账号', help='账号')
@click.option('-p', '--password', prompt='密码', help='密码')
@click.option('-s', '--signature', help='签名')
@click.option('-v', '--verbose', type=bool, default=True, show_default=True, help='输出详细过程')
def cli_logout(esurfing_url, wlan_acip, wlan_userip, account, password, signature, verbose):
    """登出校园网"""
    # account 必填参数；
    # esurfing_url, wlan_acip, wlan_userip 必填参数；
    # password, signature 至少填一项参数；
    # verbose: 选填参数，输出过程。
    return esurfing.logout(esurfingurl=esurfing_url, wlanacip=wlan_acip, wlanuserip=wlan_userip,
                           account=account, password=password, signature=signature, verbose=verbose)


@cli.command(name="auto")
@click.option('-m', '--mode', prompt='触发模式', help='触发模式', type=click.Choice(["uls", "dls", "ult", "dlt", "itv", "mul"], case_sensitive=False))
@click.option('-t', '--threshold', prompt='触发阈值', type=float, help='触发网速(MB/s)或流量(MB)或时间(s)')
@click.option('-s', '--auto-stop', prompt='自动停止', default=True, show_default=True, type=bool, help='自动停止(仅对网速模式有效)')
@click.option('-u', '--esurfing-url', default=DEFAULT_ESURFING_URL, show_default=True, help='校园网登录网址')
@click.option('-c', '--wlan-acip', help='认证服务器IP')
@click.option('-r', '--wlan-userip', help='登录设备IP')
@click.option('-a', '--account', prompt='账号', help='账号')
@click.option('-p', '--password', prompt='密码', help='密码')
@click.option('-v', '--verbose', type=bool, default=True, show_default=True, help='输出详细过程')
def cli_auto(mode, threshold, auto_stop, esurfing_url, wlan_acip, wlan_userip, account, password, verbose):
    """多种模式触发重登校园网"""
    # mode:
    #     uls, upload_speed     - 上行速率低于指定值时自动重登校园网
    #     dls, download_speed   - 下载速率低于指定值时自动重登校园网
    #     ult, upload_traffic   - 上传流量达到指定值时自动重登校园网
    #     dlt, download_traffic - 下载流量达到指定值时自动重登校园网
    #     itv, interval         - 间隔指定的时间自动重登校园网
    #     mul, manual           - 手动按回车后自动重登校园网
    # threshold: 触发阈值
    esf = esurfing.ESurfing(
        account=account,
        password=password,
        esurfingurl=esurfing_url,
        wlanacip=wlan_acip,
        wlanuserip=wlan_userip,
        verbose=verbose
    )
    return relogin(esf, mode, threshold, auto_stop)


@cli.command(name="ocr")
@click.option('-i', '--image', prompt='图片路径', help='图片路径')
def cli_ocr(image: str) -> None or str:
    """识别图片"""
    # 文件不存在
    if not os.path.isfile(image):
        click.echo("错误：目标图片文件不存在")
        return None

    # 读取图片
    try:
        with open(image, "rb") as f:
            image_bytes = f.read()
    except PermissionError:
        click.echo("读取图片失败，请确保程序具有读取权限")
        return None

    # 识别图片
    log_time = time.time()
    succeed, result = ocr_image(image_bytes)
    time_taken = round(time.time() - log_time, 2)

    # 返回结果
    if succeed:
        click.echo(f'识别成功，识别结果：{result}  耗时：{time_taken}s')
    else:
        click.echo(f'识别失败，错误信息：{result}  耗时：{time_taken}s')
    return result


@cli.command(name="version")
def cli_version():
    """输出当前版本"""
    click.echo(f"{__version__} ({__date__})")
