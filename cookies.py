# encoding=utf-8

import base64
import requests
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging
from yumdama import identify

reload(sys)
sys.setdefaultencoding('utf8')
IDENTIFY = 1 
COOKIE_GETWAY = 0 # 0 
dcap = dict(DesiredCapabilities.PHANTOMJS)  
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
)
logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING) 


myWeiBo = [
    {'no': 'jiadieyuso3319@163.com', 'psw': 'a123456'},
    {'no': 'shudieful3618@163.com', 'psw': 'a123456'},
]

def getCookie(account, password):
    if COOKIE_GETWAY == 0:
        return get_cookie_from_login_sina_com_cn(account, password)
    elif COOKIE_GETWAY ==1:
        return get_cookie_from_weibo_cn(account, password)
    else:
        logger.error("COOKIE_GETWAY Error!")

def get_cookie_from_login_sina_com_cn(account, password):
    loginURL = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)"
    username = base64.b64encode(account.encode("utf-8")).decode("utf-8")
    postData = {
        "entry": "sso",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1440*900",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }
    session = requests.Session()
    r = session.post(loginURL, data=postData)
    jsonStr = r.content.decode("gbk")
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        logger.warning("Get Cookie Success!( Account:%s )" % account)
        cookie = session.cookies.get_dict()
        return json.dumps(cookie)
    else:
        logger.warning("Failed!( Reason:%s )" % info["reason"])
        return ""


def get_cookie_from_weibo_cn(account, password):

    try:
        browser = webdriver.PhantomJS(desired_capabilities=dcap)
        browser.get("https://weibo.cn/login/")
        time.sleep(1)

        failure = 0
        while "??????" in browser.title and failure < 5:
            failure += 1
            browser.save_screenshot("aa.png")
            username = browser.find_element_by_name("mobile")
            username.clear()
            username.send_keys(account)

            psd = browser.find_element_by_xpath('//input[@type="password"]')
            psd.clear()
            psd.send_keys(password)
            try:
                code = browser.find_element_by_name("code")
                code.clear()
                if IDENTIFY == 1:
                    code_txt = raw_input("??????????????????????????????aa.png????????????????????????:")  # ?????????????????????
                else:
                    from PIL import Image
                    img = browser.find_element_by_xpath('//form[@method="post"]/div/img[@alt="?????????????????????"]')
                    x = img.location["x"]
                    y = img.location["y"]
                    im = Image.open("aa.png")
                    im.crop((x, y, 100 + x, y + 22)).save("ab.png")  # ??????????????????
                    code_txt = identify()  # ???????????????????????????
                code.send_keys(code_txt)
            except Exception, e:
                pass

            commit = browser.find_element_by_name("submit")
            commit.click()
            time.sleep(3)
            if "????????????" not in browser.title:
                time.sleep(4)
            if '???????????????' in browser.page_source:
                print '?????????????????????'
                return {}

        cookie = {}
        if "????????????" in browser.title:
            for elem in browser.get_cookies():
                cookie[elem["name"]] = elem["value"]
            logger.warning("Get Cookie Success!( Account:%s )" % account)
        return json.dumps(cookie)
    except Exception, e:
        logger.warning("Failed %s!" % account)
        return ""
    finally:
        try:
            browser.quit()
        except Exception, e:
            pass



def getCookies(weibo):
 
    cookies = []
    for elem in weibo:
        account = elem['no']
        password = elem['psw']
        cookie  =  getCookie(account, password)
        if cookie != None:
            cookies.append(cookie)

    return cookies


cookies = getCookies(myWeiBo)
logger.warning("Get Cookies Finish!( Num:%d)" % len(cookies))
