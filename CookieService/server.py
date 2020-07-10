
import json
import time
from concurrent.futures import ThreadPoolExecutor,as_completed
from functools import partial

import redis
import settings

class CookiesServer():
    # 初始化redis连接
    def __init__(self,settings):
        self.settings = settings
        self.redis_cli = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
            )
        self.service_list = []

    def register(self,cls):
        self.service_list.append(cls)

    #检查cookie池是否已满，如果没满则调用loginserver增加cookie
    def login_service(self,srv):
        while True:
            srv_name = srv.name
            cookie_nums = self.redis_cli.scard(self.settings.ACCOUNTS[srv_name]["cookie_key"])
            if cookie_nums < self.settings.ACCOUNTS[srv_name]["max_cookie_nums"]:
                srv_cli = srv(self.settings)
                cookie_dict = srv_cli.login()
                self.redis_cli.sadd(
                    self.settings.ACCOUNTS[srv_name]["cookie_key"],
                    json.dumps(cookie_dict)
                    )
            else:
                print("cookies of {srv_name} is full,wait for 10s".format(srv_name=srv_name))
                time.sleep(10)

    #检测cookie池中的cookie是否失效
    def check_cookie_service(self,srv):
        while True:
            print("checking cookies")
            srv_name = srv.name
            all_cookies = self.redis_cli.smembers(self.settings.ACCOUNTS[srv_name]["cookie_key"])
            for cookie_str in all_cookies:
                # print("get cookie: {}".format(cookie_str))
                cookie_dict = json.loads(cookie_str)
                srv_cli = srv(self.settings)
                valid = srv_cli.check_cookie(cookie_dict)
                if valid:
                    print("cookie is valid")
                else:
                    print("cookie is invalid,delete cookie")
                    self.redis_cli.srem(self.settings.ACCOUNTS[srv_name]["cookie_key"],cookie_str)
            # 防止请求频繁造成有效cookie失效，设置延时
            interval = self.settings.ACCOUNTS[srv_name]["check_interval"]
            print("after {interval}s restart check cookie".format(interval=interval))
            time.sleep(interval)

    def start(self):
        task_list = []
        print("start login service")
        login_executor = ThreadPoolExecutor(max_workers=5)
        for srv in self.service_list:
            task = login_executor.submit(partial(self.login_service,srv))
            task_list.append(task)
        # print("start check cookie")
        check_executor = ThreadPoolExecutor(max_workers=5)
        for srv in self.service_list:
            task = check_executor.submit(partial(self.check_cookie_service,srv))
            task_list.append(task)
        for future in as_completed(task_list):
            data = future.result()
