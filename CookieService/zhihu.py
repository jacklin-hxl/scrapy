
import time
import base64

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from base_service import BaseService
from selenium.webdriver.common.keys import Keys
from zheye import zheye
from mouse import move,click
from chaojiying import Chaojiying_Client

class ZhihuLoginService(BaseService):
    '''
    通过chrome.exe --remote-debugging-port=9222 结合 chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")反爬
    or
    通过chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    '''
    name = "zhihu"

    def __init__(self):
        chrome_options = Options()
        # chrome_options.headless = True
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # chrome_options.add_experimental_option('useAutomationExtension', False)
        # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.brower = webdriver.Chrome(executable_path="webdriver/chromedriver.exe",chrome_options=chrome_options)
        # self.brower.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        # "source": """
        #     Object.defineProperty(navigator, 'webdriver', {
        #         get: () => undefined
        #     })
        # """
        # })

    def check_login(self):
        try:
            time.sleep(3)
            notify_element = self.brower.find_element_by_class_name("AppHeader-userInfo")
            return True
        except Exception as e:
            return False

    def login(self):
        self.brower.get("https://www.zhihu.com/signin")
        while not self.check_login():
            login_elemet = self.brower.find_element_by_css_selector("#root > div > main > div > div > div > div.SignContainer-content > div > form > div.SignFlow-tabs > div:nth-child(2)")
            login_elemet.click()
            self.brower.find_element_by_xpath("//input[@name='username']").send_keys(Keys.CONTROL + "a")
            self.brower.find_element_by_xpath("//input[@name='username']").send_keys("18355053764")
            self.brower.find_element_by_xpath("//input[@name='password']").send_keys(Keys.CONTROL + "a")
            self.brower.find_element_by_xpath("//input[@name='password']").send_keys("2468gggg")
            botton = self.brower.find_element_by_css_selector(".Button.SignFlow-submitButton.Button--primary.Button--blue")
            try:
                chimgcode = "null"
                chinese_captcha_element = self.brower.find_element_by_class_name("Captcha-chineseImg")
                base64_text = chinese_captcha_element.get_attribute("src")
                chimgcode = base64_text.replace("data:image/jpg;base64,","").replace("%0A","")
            except:
                pass
            try:
                enimgcode = "null"
                englsh_captcha_element = self.brower.find_element_by_class_name("Captcha-englishImg")
                base64_text = englsh_captcha_element.get_attribute("src")
                enimgcode = base64_text.replace("data:image/jpg;base64,","").replace("%0A","")
            except:
                pass
            if chimgcode != "null":
                with open("captcha/chincaptcha.jpeg","wb") as f:
                    f.write(base64.b64decode(enimgcode))
                ele_postion = chinese_captcha_element.location
                x_relative = ele_postion["x"]
                y_relative = ele_postion["y"]
                brower_navigation_panel_height = self.brower.execute_script(
                    "return window.outerHeight - window.innerHeight;"
                )
                z = zheye()
                positions = z.Recognize('captcha/chincaptcha.jpeg')
                last_position = []
                if len(positions) == 2:
                    last_position.append([positions[0][1],positions[0][0]])
                    last_position.append([positions[1][1],positions[1][0]])
                    first_position = [int(last_position[0][0] / 2),int(last_position[0][1] / 2)]
                    second_position = [int(last_position[1][0] / 2),int(last_position[1][1] / 2)]
                    move(x_relative + first_position[0],
                    y_relative + brower_navigation_panel_height + first_position[1]
                    )
                    click()
                    move(x_relative + second_position[0],
                    y_relative + brower_navigation_panel_height + second_position[1]
                    )
                    click()
                elif len(positions) == 1:
                    last_position.append([positions[0][1],positions[0][0]])
                    first_position = [int(last_position[0][0] / 2),int(last_position[0][1] / 2)]
                    move(x_relative + first_position[0],
                    y_relative + brower_navigation_panel_height + first_position[1]
                    )
                    click()
            elif enimgcode != "null":
                with open("captcha/engcaptcha.jpeg","wb") as f:
                    f.write(base64.b64decode(enimgcode))
                chaojiyingapi = Chaojiying_Client("hxltest","2468gggg","906234")
                im = open('captcha/engcaptcha.jpeg', 'rb').read()
                json_result = chaojiyingapi.PostPic(im,1902)
                if json_result["err_no"] == 0:
                    pic_str = json_result["pic_str"]
                    print("识别码：{pic_str}".format(pic_str=pic_str))
                else:
                    print("识别失败")
                    pic_str = "null"
                self.brower.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/div/label/input').send_keys(pic_str)
            botton.click()
        cookies = self.brower.get_cookies()
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']
        self.brower.close()
        return cookies_dict


if __name__ == "__main__":
    a = ZhihuLoginService()
    a.login()