import json
import os
import platform
import webbrowser
from tkinter import messagebox as msgbox

import ttkbootstrap as ttk

from . import esurfing
from .__version__ import __version__, __url__, __date__

DEFAULT_CONF_FILE = "./ESurfingPy-CLI.json"


class Gui:
    def __init__(self, hide_console: bool = False):
        """init"""

        data = self.read_conf()
        self.signature = data.get("signature")

        self.toplevel = ttk.Window(themename="lumen")
        self.toplevel.configure(width=200)
        self.toplevel.resizable(False, False)
        self.toplevel.title(f"ESurfingPy-CLI v{__version__}")

        self.frame1 = ttk.Frame(self.toplevel)
        self.frame1.configure(padding=10)
        self.frame2 = ttk.Frame(self.frame1)
        self.frame2.configure(height=200)

        self.label_u = ttk.Label(self.frame2)
        self.label_u.configure(text='请求网址')
        self.label_u.grid(column=0, row=0, sticky="e")
        self.entry_u = ttk.Entry(self.frame2)
        self.entry_u.insert("0", data.get("esurfingurl", "enet.10000.gd.cn:10001"))
        self.entry_u.grid(column=1, padx=5, pady=2, row=0)

        self.button_get_params = ttk.Button(self.frame2)
        self.button_get_params.configure(text='\n尝试获取\n本机信息\n')
        self.button_get_params.grid(column=2, row=0, rowspan=3)
        self.button_get_params.configure(command=self.get_params)

        self.label_c = ttk.Label(self.frame2)
        self.label_c.configure(text='认证服务器 IP')
        self.label_c.grid(column=0, row=1)
        self.entry_c = ttk.Entry(self.frame2)
        self.entry_c.insert("0", data.get("wlanacip", ""))
        self.entry_c.grid(column=1, padx=5, pady=2, row=1)

        self.label_r = ttk.Label(self.frame2)
        self.label_r.configure(text='登录设备 IP')
        self.label_r.grid(column=0, row=2, sticky="e")
        self.entry_r = ttk.Entry(self.frame2)
        self.entry_r.insert("0", data.get("wlanuserip", ""))
        self.entry_r.grid(column=1, padx=5, pady=2, row=2)

        self.label_a = ttk.Label(self.frame2)
        self.label_a.configure(text='账号')
        self.label_a.grid(column=0, row=3, sticky="e")
        self.entry_a = ttk.Entry(self.frame2)
        self.entry_a.insert("0", data.get("account", ""))
        self.entry_a.grid(column=1, padx=5, pady=2, row=3)

        self.label_p = ttk.Label(self.frame2)
        self.label_p.configure(text='密码')
        self.label_p.grid(column=0, row=4, sticky="e")
        self.entry_p = ttk.Entry(self.frame2)
        self.entry_p.configure(show="•")
        self.entry_p.insert("0", data.get("password", ""))
        self.entry_p.grid(column=1, padx=5, pady=2, row=4)

        self.var_save = ttk.BooleanVar(value=True)
        self.checkbutton_save = ttk.Checkbutton(self.frame2, variable=self.var_save)
        self.checkbutton_save.configure(text='保存信息')
        self.checkbutton_save.grid(column=1, row=5, pady=10)

        self.frame2.pack(side="top")
        self.frame3 = ttk.Frame(self.frame1)

        self.button_login = ttk.Button(self.frame3)
        self.button_login.configure(text='登录')
        self.button_login.pack(padx=5, side="left")
        self.button_login.configure(command=self.login)

        self.button_logout = ttk.Button(self.frame3)
        self.button_logout.configure(text='登出')
        self.button_logout.pack(padx=5, side="left")
        self.button_logout.configure(command=self.logout)

        self.frame3.pack(side="top")
        self.separator = ttk.Separator(self.frame1)
        self.separator.configure(orient="horizontal")
        self.separator.pack(expand=True, fill="both", pady=8)
        self.frame4 = ttk.Frame(self.frame1)

        # show and hide console (Windows only)
        self.console_visible = True
        if platform.system() == "Windows":
            import ctypes
            self.button_toggle_console = ttk.Button(self.frame4)
            self.button_toggle_console.configure(text="隐藏控制台")
            self.button_toggle_console.pack(padx=5, side="left")
            self.button_toggle_console.configure(command=self.toggle_console)
            if hide_console:
                self.toggle_console()

        self.button_about = ttk.Button(self.frame4)
        self.button_about.configure(text='关于')
        self.button_about.pack(padx=5, side="left")
        self.button_about.configure(command=self.about)
        self.frame4.pack(side="top")
        self.frame1.pack(side="top")

        self.window = self.toplevel

    def run(self):
        self.window.mainloop()

    @staticmethod
    def read_conf() -> dict:
        """读取配置"""
        if os.path.isfile(DEFAULT_CONF_FILE):
            try:
                with open(DEFAULT_CONF_FILE, encoding="utf-8") as f:
                    return json.loads(f.read())
            except json.JSONDecodeError:
                pass
        return {}

    def save_conf(self) -> bool:
        """保存配置"""
        try:
            with open(DEFAULT_CONF_FILE, "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "esurfingurl": self.entry_u.get(),
                    "wlanacip": self.entry_c.get(),
                    "wlanuserip": self.entry_r.get(),
                    "account": self.entry_a.get(),
                    "password": self.entry_p.get(),
                    "signature": self.signature
                }, indent=4))
                return True
        except PermissionError:
            msgbox.showwarning(
                title="警告",
                message="保存信息失败，可能的原因："
                        "\n1. 程序权限不足"
                        "\n2. 文件已被占用"
            )
        except Exception as exc:
            msgbox.showwarning(
                title="警告",
                message=f"保存信息失败，原因："
                        f"\n{exc}"
            )
        return False

    def get_params(self) -> bool:
        """获取参数"""
        success, esurfingurl, wlanacip, wlanuserip = esurfing.get_parameters()
        if not success:
            msgbox.showerror(
                title="错误",
                message="获取本机参数失败，可能的原因："
                        "\n1. 未连接校园网"
                        "\n2. 当前已登录校园网"
            )
            return False
        for entry, value in [
            (self.entry_u, esurfingurl),
            (self.entry_c, wlanacip),
            (self.entry_r, wlanuserip)
        ]:
            entry.delete(0, ttk.END)
            entry.insert(0, value)
        return True

    def login(self):
        """登录"""
        if self.var_save.get():
            self.save_conf()
        success, msg_or_signature = esurfing.login(
            account=self.entry_a.get(),
            password=self.entry_p.get(),
            esurfingurl=self.entry_u.get(),
            wlanacip=self.entry_c.get(),
            wlanuserip=self.entry_r.get(),
        )
        if success:
            self.signature = msg_or_signature
            self.button_logout.configure(state=ttk.NORMAL)
            msgbox.showinfo("提示", "登录成功")
        else:
            msgbox.showerror("提示", f"登录失败：{msg_or_signature}")

    def logout(self):
        """登出"""
        success, msg = esurfing.logout(
            account=self.entry_a.get(),
            password=self.entry_p.get(),
            esurfingurl=self.entry_u.get(),
            wlanacip=self.entry_c.get(),
            wlanuserip=self.entry_r.get(),
            signature=self.signature
        )
        if success:
            msgbox.showinfo("提示", "登出成功")
        else:
            msgbox.showerror("提示", f"登出失败：{msg}")

    def toggle_console(self):
        """切换显示或隐藏控制台（仅适用于 Windows）"""
        if platform.system() == "Windows":
            import ctypes
            self.console_visible = not self.console_visible
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), self.console_visible)
            self.button_toggle_console.configure(text=("隐藏" if self.console_visible else "显示") + "控制台")

    @staticmethod
    def about():
        """关于"""
        open_url = msgbox.askyesno(
            title="关于",
            message=f"版本：{__version__} ({__date__})"
                    f"\n项目：{__url__}"
                    f"\n"
                    f"\nESurfingPy-CLI 为命令行工具，"
                    f"\n此图形界面仅提供登录和登出功能，"
                    f"\n完整功能需使用命令行调用此程序。"
                    f"\n"
                    f"\n完整文档、反馈问题等请到 GitHub，"
                    f"\n是否打开项目链接？"
        )
        if open_url:
            webbrowser.open(__url__)


if __name__ == "__main__":
    Gui().run()
