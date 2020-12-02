import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from time import sleep
import subprocess
import base64
import json
import winreg
import os

def run_dnf(p, r):
    try:
        p.set("드라이버 설정...")
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36")

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument("--log-level=3")
        options.add_argument('window-size=1920x1080')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        with open("res/config.json", 'r') as f:
            config = json.loads(f.read())
        
        try:
            driver = webdriver.Chrome('res/chromedriver.exe', options=options)
        except selenium.common.exceptions.WebDriverException:
            r.set(-2)
            return

        p.set("로그인 시도..")
        if config['login_type'] == 0:
            driver.get(r"https://login.df.nexon.com/df/member/login")
            driver.find_element_by_id('id').send_keys(config['id'])
            driver.find_element_by_id('pw').send_keys(config['pw'])
            driver.find_element_by_id('loginForm').submit()
            driver.implicitly_wait(1)
            if driver.find_elements_by_css_selector(".login_apart_2018 .la_content ul li.txt"):
                r.set(-3)
                return
        elif config['login_type'] == 1:
            driver.get(r"https://nxlogin.nexon.com/common/login.aspx?redirect=http%3a%2f%2fdf.nexon.com%2fdf%2fhome")
            driver.find_element_by_id('txtNexonID').send_keys(config['id'])
            driver.find_element_by_id('txtPWD').send_keys(config['pw'])
            driver.find_element_by_id('btnLogin').click()
            driver.implicitly_wait(1)
            result = driver.find_elements_by_css_selector(".loginSec .loginMsg")
            if result:
                if result[0].text != '':
                    r.set(-3)
                    return
        
        p.set("토큰 수신...")
        try:
            WebDriverWait(driver, 3).until(lambda driver: "http://df.nexon.com/df" in driver.current_url)
            driver.get("http://df.nexon.com/FRM/home/game/gamePlay.php")
            param = driver.execute_script("return launcherParameters")
        except selenium.common.exceptions.JavascriptException:
            r.set(-4)
            return
        finally:
            pass
            driver.quit()

        token = ''
        for key, value in param.items():
            token += f"{key}={value}&"

        token = token[:-1]
        token = "neople://dnfreal?" + base64.b64encode(bytes(token, 'UTF-8')).decode('UTF-8')
        
        neople_protocol = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "Neople")
        neople_plugin_path, _ = winreg.QueryValueEx(neople_protocol, "Path")

        try:
            subprocess.run([os.path.join(neople_plugin_path, "NeopleCustomURLStarter.exe"), token])
            r.set(0)
            return
        except OSError:
            r.set(-5)
            return
    except Exception as e:
        print(e)
        r.set(-6)
        return
