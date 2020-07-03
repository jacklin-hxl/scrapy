#超级鹰配置
CJY_UNAME = "hxltest"
CJY_PASSWD = "2468gggg"

#redis配置
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379

#爬取网站登录信息
ACCOUNTS = {
    "zhihu":{
        "username":"18355053764",
        "password":"2468gggg",
        "cookie_key":"zhihu:cookies",
        "max_cookie_nums":5,
        "check_interval":30,
    }
}