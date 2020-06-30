
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from base_service import BaseService
from selenium.webdriver.common.keys import Keys

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
        self.brower = webdriver.Chrome(executable_path="webdriver/chromedriver.exe",chrome_options=chrome_options,options=option)
        # self.brower.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        # "source": """
        #     Object.defineProperty(navigator, 'webdriver', {
        #         get: () => undefined
        #     })
        # """
        # })

    def check_login(self):
        try:
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
            # self.brower.find_element_by_xpath("//form//botton[@type='submit']").click()
            botton = self.brower.find_element_by_css_selector(".Button.SignFlow-submitButton.Button--primary.Button--blue")
            botton.click()
            time.sleep(5)
            print(self.brower.page_source)

if __name__ == "__main__":
    a = ZhihuLoginService()
    a.login()