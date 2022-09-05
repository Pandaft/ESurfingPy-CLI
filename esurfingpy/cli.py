import click
from . import esurfing

DEFAULT_ESURFING_URL = "enet.10000.gd.cn:10001"


@click.group()
def cli():
    """(v0.19) 基于 Python 实现登录和登出广东天翼校园网网页认证通道的命令行工具。"""
    pass


@cli.command()
@click.option('-url', '--esurfingurl', prompt='ESurfingUrl', default=DEFAULT_ESURFING_URL, help='校园网登录网址')
@click.option('-acip', '--wlanacip', prompt='WlanAcIP', default='', help='认证服务器IP')
@click.option('-userip', '--wlanuserip', prompt='WlanUserIP', default='', help='登录设备IP')
@click.option('-acc', '--account', prompt='Account', help='账号')
@click.option('-pwd', '--password', prompt='Password', help='密码')
@click.option('-detail', prompt='Detail', type=bool, default=True, help='输出详细过程')
def login(esurfingurl, wlanacip, wlanuserip, account, password, detail):
    """登录校园网"""
    # account, password 必填参数；
    # esurfingurl, wlanacip, wlanuserip 选填参数，本机登录且未登录时可自动获取；
    # detail: 选填参数，输出过程。
    return esurfing.login(esurfingurl=esurfingurl, wlanacip=wlanacip, wlanuserip=wlanuserip,
                          account=account, password=password, detail=detail)


@cli.command()
@click.option('-url', '--esurfingurl', prompt='ESurfingUrl', default=DEFAULT_ESURFING_URL, help='校园网登录网址')
@click.option('-acip', '--wlanacip', prompt='WlanAcIP', default='', help='认证服务器IP')
@click.option('-userip', '--wlanuserip', prompt='WlanUserIP', default='', help='登录设备IP')
@click.option('-acc', '--account', prompt='Account', help='账号')
@click.option('-pwd', '--password', prompt='Password', default='', help='密码')
@click.option('-sign', '--signature', prompt='Signature', default='', help='签名')
@click.option('-detail', prompt='Detail', type=bool, default=True, help='输出详细过程')
def logout(esurfingurl, wlanacip, wlanuserip, account, password, signature, detail):
    """登出校园网"""
    # account 必填参数；
    # esurfingurl, wlanacip, wlanuserip 必填参数；
    # password, signature 至少填一项参数；
    # detail: 选填参数，输出过程。
    return esurfing.logout(esurfingurl=esurfingurl, wlanacip=wlanacip, wlanuserip=wlanuserip,
                           account=account, password=password, signature=signature, detail=detail)


@cli.command()
@click.option('-m', '--mode', prompt='Mode', default="0", help='触发模式')
@click.option('-v', '--value', prompt='Value', default="0", help='触发网速(MB/s)或流量(MB)或时间(s)')
@click.option('-as', '--autostop', prompt='AutoStop', default=True, type=bool, help='自动停止')
@click.option('-url', '--esurfingurl', prompt='ESurfingURL', default=DEFAULT_ESURFING_URL, help='校园网登录网址')
@click.option('-acip', '--wlanacip', prompt='WlanACIP', default="", help='认证服务器IP')
@click.option('-userip', '--wlanuserip', prompt='WlanUserIP', default="", help='登录设备IP')
@click.option('-acc', '--account', prompt='Account', help='账号')
@click.option('-pwd', '--password', prompt='Password', help='密码')
@click.option('-detail', prompt='Detail', default=False, type=bool, help='输出详细过程')
def auto(mode, value, autostop, esurfingurl, wlanacip, wlanuserip, account, password, detail):
    """
    多种模式触发重登校园网
    mode:
        uls, upload_speed     - 上行速率低于指定值时自动重登校园网
        dls, download_speed   - 下载速率低于指定值时自动重登校园网
        ult, upload_traffic   - 上传流量达到指定值时自动重登校园网
        dlt, download_traffic - 下载流量达到指定值时自动重登校园网
        itv, interval         - 间隔指定的时间自动重登校园网
        mul, manual           - 手动按回车后自动重登校园网
    value: 指定值
    """
    esf = esurfing.ESurfing(
        account=account,
        password=password,
        esurfingurl=esurfingurl,
        wlanacip=wlanacip,
        wlanuserip=wlanuserip,
        detail=detail,
    )
    return auto.relogin(esf, mode, value, autostop)


@cli.command()
@click.option('-img', '--imagefile', prompt='Image File:', help='图片路径')
def ocr(imagefile):
    """识别验证码"""
    succeed, result = ocr.ocr_img(imagefile)
    if succeed:
        click.echo(f'识别成功，识别结果：{result}')
    else:
        click.echo(f'识别失败，错误信息：{result}')
    return result
