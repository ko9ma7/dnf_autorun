import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import json
import os
from autorun import run_dnf
from threading import Thread

class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.end_msg = [
            "런처 실행중...",
            "유효하지 않은 설정",
            "크롬 드라이버를 찾을 수 없음",
            "아이디, 비밀번호 인증 실패",
            "토큰 가져오기 실패",
            "관리자 권한 필요",
            "알 수 없는 오류"
        ]
        self.user_id = tk.StringVar()
        self.user_pw = tk.StringVar()
        self.login_type = tk.IntVar()
        self.progress = tk.StringVar()
        self.r = tk.IntVar()
        self.run_dnf_thread = 0

        self.r.set(1)
        if os.path.isfile("res/config.json"):
            with open("res/config.json", 'r') as f:
                config = json.load(f)
            self.user_id.set(config['id'])
            self.user_pw.set(config['pw'])
            self.login_type.set(config['login_type'])

        tk.Label(self, text="ID").place(x=13, y=10)
        tk.Label(self, text="PW").place(x=7, y=32)

        self.idField = ttk.Entry(self, width=22, textvariable=self.user_id)
        self.idField.place(x=40, y=10)

        self.pwField = ttk.Entry(self, width=22, show="*", textvariable=self.user_pw)
        self.pwField.place(x=40, y=32)

        self.login_type_dnf_radio = ttk.Radiobutton(self, text="던파 ID", variable=self.login_type, value=0)
        self.login_type_dnf_radio.place(x=37, y=54)
        self.login_type_nexon_radio = ttk.Radiobutton(self, text="넥슨 ID", variable=self.login_type, value=1)
        self.login_type_nexon_radio.place(x=110, y=54)

        self.submit_btn = ttk.Button(self, text="확인", command=self.onSubmit)
        self.submit_btn.place(x=200, y=9, height=45, width=44)

        self.p = tk.Label(self, textvariable=self.progress)
        self.p.place(x=36, y=76)
    
    def change_form_state(self, state):
        self.login_type_dnf_radio.config(state=state)
        self.login_type_nexon_radio.config(state=state)
        self.idField.config(state=state)
        self.pwField.config(state=state)
        self.submit_btn.config(state=state)

    def check_done(self):
        result = self.r.get()
        if result != 1:
            self.run_dnf_thread.join()
            result = -result
            self.progress.set(self.end_msg[result])
            if result == 0:
                self.destroy()
            else:
                self.p.config(fg="red")

            self.change_form_state("nomal")
            return
        self.after(100, self.check_done)

    def onSubmit(self):
        self.p.config(fg="black")
        self.r.set(1)
        self.change_form_state("disabled")
        self.progress.set("pre")
        config = {
            'id': self.user_id.get(),
            'pw': self.user_pw.get(),
            'login_type': self.login_type.get()
        }
        with open("res/config.json", 'w') as f:
            json.dump(config, f)
        self.run_dnf_thread = Thread(target = run_dnf, args=[self.progress, self.r])
        self.run_dnf_thread.start()
        self.check_done()

root = GUI()
root.title("DNF starter")
root.geometry("255x108")
root.resizable(False, False)
root.mainloop()