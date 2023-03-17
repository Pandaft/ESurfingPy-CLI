import os
import json
import webbrowser
from tkinter import messagebox as msgbox

import ttkbootstrap as ttk

from . import esurfing
from .__version__ import __version__, __url__, __date__

DEFAULT_DATA_FILE = "./ESurfingPy-cli.json"


class Gui:
    def __init__(self):
        """init"""
        data = self.read_data()

        self.toplevel = ttk.Window(themename="lumen")
        self.toplevel.configure(width=200)
        self.toplevel.resizable(False, False)
        self.toplevel.title("GUI for ESurfingPy-CLI")
        self.frame2 = ttk.Frame(self.toplevel)
        self.frame2.configure(padding=10)
        self.frame1 = ttk.Frame(self.frame2)
        self.frame1.configure(height=200)
        self.label_u = ttk.Label(self.frame1)
        self.label_u.configure(text='请求网址')
        self.label_u.grid(column=0, row=0, sticky="e")
        self.entry_u = ttk.Entry(self.frame1)
        self.entry_u.insert("0", data.get("esurfingurl", "enet.10000.gd.cn:10001"))
        self.entry_u.grid(column=1, padx=5, pady=2, row=0)
        self.button_get_params = ttk.Button(self.frame1)
        self.button_get_params.configure(text='\n尝试获取\n本机信息\n')
        self.button_get_params.grid(column=2, row=0, rowspan=3)
        self.button_get_params.configure(command=self.get_params)
        self.label_c = ttk.Label(self.frame1)
        self.label_c.configure(text='认证服务器 IP')
        self.label_c.grid(column=0, row=1)
        self.entry_c = ttk.Entry(self.frame1)
        self.entry_c.insert("0", data.get("wlanacip", ""))
        self.entry_c.grid(column=1, padx=5, pady=2, row=1)
        self.label_r = ttk.Label(self.frame1)
        self.label_r.configure(text='登录设备 IP')
        self.label_r.grid(column=0, row=2, sticky="e")
        self.entry_r = ttk.Entry(self.frame1)
        self.entry_r.insert("0", data.get("wlanuserip", ""))
        self.entry_r.grid(column=1, padx=5, pady=2, row=2)
        self.label_a = ttk.Label(self.frame1)
        self.label_a.configure(text='账号')
        self.label_a.grid(column=0, row=3, sticky="e")
        self.entry_a = ttk.Entry(self.frame1)
        self.entry_a.insert("0", data.get("account", ""))
        self.entry_a.grid(column=1, padx=5, pady=2, row=3)
        self.label_p = ttk.Label(self.frame1)
        self.label_p.configure(text='密码')
        self.label_p.grid(column=0, row=4, sticky="e")
        self.entry_p = ttk.Entry(self.frame1)
        self.entry_p.configure(show="•")
        self.entry_p.insert("0", data.get("password", ""))
        self.entry_p.grid(column=1, padx=5, pady=2, row=4)
        self.checkbutton_save = ttk.Checkbutton(self.frame1)
        self.checkbutton_save.configure(text='保存信息')
        # self.checkbutton_save.state(('selected', ))  # IDK why it doesn't work :(
        self.checkbutton_save.grid(column=1, row=5, pady=5)
        self.frame1.pack(ipady=5, side="top")
        self.frame3 = ttk.Frame(self.frame2)
        self.button_login = ttk.Button(self.frame3)
        self.button_login.configure(text='登录')
        self.button_login.grid(column=0, padx=10, row=0)
        self.button_login.configure(command=self.login)
        # self.button_logout = ttk.Button(self.frame3)  # To be develop
        # self.button_logout.configure(state="disabled", text='登出')
        # self.button_logout.grid(column=1, padx=10, row=0)
        # self.button_logout.configure(command=self.logout)
        self.button4 = ttk.Button(self.frame3)
        self.button4.configure(text='关于')
        self.button4.grid(column=2, padx=10, row=0)
        self.button4.configure(command=self.about)
        self.frame3.pack(side="top")
        self.frame2.pack(side="top")
        self.window = self.toplevel

    def run(self):
        self.window.mainloop()

    @staticmethod
    def read_data() -> dict:
        """读取数据"""
        if os.path.isfile(DEFAULT_DATA_FILE):
            try:
                with open(DEFAULT_DATA_FILE, encoding="utf-8") as f:
                    return json.loads(f.read())
            except json.JSONDecodeError:
                pass
        return {}

    def save_data(self) -> bool:
        """保存数据"""
        try:
            with open(DEFAULT_DATA_FILE, "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "esurfingurl": self.entry_u.get(),
                    "wlanacip": self.entry_c.get(),
                    "wlanuserip": self.entry_r.get(),
                    "account": self.entry_a.get(),
                    "password": self.entry_p.get(),
                    # "save": self.checkbutton_save.state() == ('selected',)
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
        if self.checkbutton_save.state() == ("selected",):
            self.save_data()
        success, msg_or_signature = esurfing.login(
            account=self.entry_a.get(),
            password=self.entry_p.get(),
            esurfingurl=self.entry_u.get(),
            wlanacip=self.entry_c.get(),
            wlanuserip=self.entry_r.get(),
        )
        if success:
            # self.button_login.configure(state=tk.DISABLED)
            msgbox.showinfo("提示", "登录成功")
        else:
            msgbox.showerror("提示", f"登录失败：{msg_or_signature}")

    # def logout(self):
    #     pass

    @staticmethod
    def about():
        """关于"""
        open_url = msgbox.askyesno(
            title="关于",
            message=f"版本：{__version__} ({__date__})"
                    f"\n项目：{__url__}"
                    f"\n"
                    f"\nESurfingPy-CLI 为命令行工具，"
                    f"\n此可视化界面目前仅开发了简单的登录功能，"
                    f"\n完整功能请使用命令调用此程序。"
                    f"\n"
                    f"\n完整文档、反馈问题等请到 GitHub 项目链接，"
                    f"\n是否打开项目链接？"
        )
        if open_url:
            webbrowser.open(__url__)


if __name__ == "__main__":
    Gui().run()
